use oxidize_pdf::{Page, CoordinateSystem};
use oxidize_pdf::coordinate_system::TransformMatrix;
use oxidize_pdf::page::LayoutManager;
fn main() {
    let mut page = Page::new(200.0, 200.0);
    page.set_margins(10.0, 10.0, 10.0, 10.0);
    let mut pdf = LayoutManager::new(&page, CoordinateSystem::PdfStandard);
    println!("PDF: before={} height=40 spacing={}", pdf.current_y, pdf.element_spacing);
    println!("PDF: returned={:?} after={}", pdf.add_element(40.0), pdf.current_y);
    let mut custom = LayoutManager::new(&page, CoordinateSystem::Custom(TransformMatrix::IDENTITY));
    for i in 0..4 {
        println!("custom {i}: position={:?} current_y={} remaining={}", custom.add_element(80.0), custom.current_y, custom.remaining_space());
    }
    assert!(custom.current_y < 0.0);
    assert!(custom.will_fit(80.0));
}
