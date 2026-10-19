//! Lossless mapping of core events, including binary streams and parsed objects.
use crate::signing::{dictionary_values, PyPdfValue};
use oxidize_pdf::streaming::ParseEvent;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

pub(crate) fn event_to_dict(py: Python<'_>, event: ParseEvent) -> PyResult<Bound<'_, PyDict>> {
    let dict = PyDict::new(py);
    match event {
        ParseEvent::Header { version } => {
            dict.set_item("type", "header")?;
            dict.set_item("version", version)?;
        }
        ParseEvent::ObjectStart { id, generation } => {
            dict.set_item("type", "object_start")?;
            dict.set_item("id", id)?;
            dict.set_item("generation", generation)?;
        }
        ParseEvent::ObjectEnd {
            id,
            generation,
            object,
        } => {
            dict.set_item("type", "object_end")?;
            dict.set_item("id", id)?;
            dict.set_item("generation", generation)?;
            dict.set_item("object", PyPdfValue { inner: object })?;
        }
        ParseEvent::StreamData { object_id, data } => {
            dict.set_item("type", "stream_data")?;
            dict.set_item("object_id", object_id)?;
            dict.set_item("data_len", data.len())?;
            dict.set_item("data", PyBytes::new(py, &data))?;
        }
        ParseEvent::XRef { entries } => {
            dict.set_item("type", "xref")?;
            dict.set_item("entry_count", entries.len())?;
            let values = entries
                .into_iter()
                .map(|entry| {
                    let value = PyDict::new(py);
                    value.set_item("object_number", entry.object_number)?;
                    value.set_item("generation", entry.generation)?;
                    value.set_item("offset", entry.offset)?;
                    value.set_item("in_use", entry.in_use)?;
                    Ok(value)
                })
                .collect::<PyResult<Vec<_>>>()?;
            dict.set_item("entries", values)?;
        }
        ParseEvent::Trailer { dict: trailer } => {
            dict.set_item("type", "trailer")?;
            dict.set_item("dict", dictionary_values(&trailer))?;
        }
        ParseEvent::EndOfFile => dict.set_item("type", "end_of_file")?,
    }
    Ok(dict)
}

#[cfg(test)]
mod tests {
    use super::*;
    use oxidize_pdf::parser::{PdfDictionary, PdfObject};
    use oxidize_pdf::streaming::incremental_parser::XRefEntry;
    use pyo3::types::PyList;

    // These tests inject actual Rust events into the production converter.
    // They do not claim that core feed() emits XRef or Trailer today.
    #[test]
    fn preserves_nonempty_xref_and_large_offsets() {
        Python::initialize();
        Python::attach(|py| {
            let event = event_to_dict(
                py,
                ParseEvent::XRef {
                    entries: vec![
                        XRefEntry {
                            object_number: 42,
                            generation: 7,
                            offset: u64::MAX,
                            in_use: true,
                        },
                        XRefEntry {
                            object_number: 0,
                            generation: 65535,
                            offset: 0,
                            in_use: false,
                        },
                    ],
                },
            )
            .unwrap();
            assert_eq!(
                event
                    .get_item("entry_count")
                    .unwrap()
                    .unwrap()
                    .extract::<usize>()
                    .unwrap(),
                2
            );
            assert_eq!(
                event
                    .get_item("type")
                    .unwrap()
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "xref"
            );
            let entries = event.get_item("entries").unwrap().unwrap();
            let entries = entries.cast::<PyList>().unwrap();
            assert_eq!(entries.len(), 2);
            let first = entries.get_item(0).unwrap();
            for (key, expected) in [
                ("object_number", 42),
                ("generation", 7),
                ("offset", u64::MAX),
            ] {
                assert_eq!(
                    first.get_item(key).unwrap().extract::<u64>().unwrap(),
                    expected
                );
            }
            assert!(first.get_item("in_use").unwrap().extract::<bool>().unwrap());
            let second = entries.get_item(1).unwrap();
            assert_eq!(
                second
                    .get_item("generation")
                    .unwrap()
                    .extract::<u16>()
                    .unwrap(),
                65535
            );
            assert!(!second
                .get_item("in_use")
                .unwrap()
                .extract::<bool>()
                .unwrap());
        });
    }

    #[test]
    fn preserves_trailer_and_nonplaceholder_object() {
        Python::initialize();
        Python::attach(|py| {
            let mut trailer = PdfDictionary::new();
            trailer.insert("Root".into(), PdfObject::Reference(42, 7));
            trailer.insert("Size".into(), PdfObject::Integer(123));
            let event = event_to_dict(py, ParseEvent::Trailer { dict: trailer }).unwrap();
            assert_eq!(
                event
                    .get_item("type")
                    .unwrap()
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "trailer"
            );
            let values = event.get_item("dict").unwrap().unwrap();
            assert_eq!(
                values
                    .get_item("Root")
                    .unwrap()
                    .getattr("value")
                    .unwrap()
                    .extract::<(u32, u16)>()
                    .unwrap(),
                (42, 7)
            );
            assert_eq!(
                values
                    .get_item("Size")
                    .unwrap()
                    .getattr("value")
                    .unwrap()
                    .extract::<i64>()
                    .unwrap(),
                123
            );
            let event = event_to_dict(
                py,
                ParseEvent::ObjectEnd {
                    id: 17,
                    generation: 3,
                    object: PdfObject::Integer(i64::MIN),
                },
            )
            .unwrap();
            assert_eq!(
                event
                    .get_item("id")
                    .unwrap()
                    .unwrap()
                    .extract::<u32>()
                    .unwrap(),
                17
            );
            assert_eq!(
                event
                    .get_item("generation")
                    .unwrap()
                    .unwrap()
                    .extract::<u16>()
                    .unwrap(),
                3
            );
            assert_eq!(
                event
                    .get_item("type")
                    .unwrap()
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "object_end"
            );
            let object = event.get_item("object").unwrap().unwrap();
            assert_eq!(
                object.getattr("kind").unwrap().extract::<String>().unwrap(),
                "integer"
            );
            assert_eq!(
                object.getattr("value").unwrap().extract::<i64>().unwrap(),
                i64::MIN
            );
        });
    }

    #[test]
    fn preserves_binary_stream_bytes_without_decoding() {
        Python::initialize();
        Python::attach(|py| {
            let data = vec![0, 255, b' ', b'\n', 128];
            let event = event_to_dict(
                py,
                ParseEvent::StreamData {
                    object_id: 9,
                    data: data.clone(),
                },
            )
            .unwrap();
            assert_eq!(
                event
                    .get_item("type")
                    .unwrap()
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "stream_data"
            );
            let value = event.get_item("data").unwrap().unwrap();
            assert_eq!(value.cast::<PyBytes>().unwrap().as_bytes(), data);
            assert_eq!(
                event
                    .get_item("data_len")
                    .unwrap()
                    .unwrap()
                    .extract::<usize>()
                    .unwrap(),
                data.len()
            );
            assert_eq!(
                event
                    .get_item("object_id")
                    .unwrap()
                    .unwrap()
                    .extract::<u32>()
                    .unwrap(),
                9
            );
        });
    }
}
