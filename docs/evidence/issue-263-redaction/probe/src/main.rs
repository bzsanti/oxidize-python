use oxidize_pdf::operations::semantic_redactor::{SemanticRedactor, RedactionConfig};
use oxidize_pdf::semantic::{SemanticEntity, EntityType, BoundingBox};
fn main() {
    let args: Vec<_> = std::env::args().collect();
    let input = std::fs::read(&args[1]).unwrap();
    let entity = SemanticEntity::new("secret".to_string(), EntityType::Text, BoundingBox::new(10., 60., 150., 30., 1)).with_content("SECRET");
    match SemanticRedactor::redact_irreversible(&input, &[entity], RedactionConfig::new().with_types(vec![EntityType::Text])) {
        Ok((bytes, report)) => { println!("irreversible={} risks={:?}", report.is_irreversible(), report.residual_risks()); std::fs::write(&args[2], bytes).unwrap(); },
        Err(e) => { eprintln!("{e}"); std::process::exit(1); }
    }
}
