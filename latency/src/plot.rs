use std::path::Path;

use hdrhistogram::Histogram;
use plotters::chart::ChartBuilder;
use plotters::chart::LabelAreaPosition;
use plotters::drawing::IntoDrawingArea as _;
use plotters::element::Rectangle;
use plotters::series::LineSeries;
use plotters::style::AsRelative as _;
use plotters::style::Color as _;
use plotters::style::Palette as _;
use plotters::style::Palette99;
use plotters::style::BLACK;
use plotters::style::WHITE;

pub fn plot<P>(path: P, data: &[(u32, Histogram<u32>)]) -> anyhow::Result<()>
where
    P: AsRef<Path>,
{
    let root = plotters::backend::SVGBackend::new(&path, (1920, 1080)).into_drawing_area();
    root.fill(&WHITE)?;

    let max_latency = data
        .iter()
        .map(|(_, histogram)| histogram)
        .filter(|histogram| !histogram.is_empty())
        .map(|histogram| histogram.max())
        .max()
        .expect("Expected maximum histogram value");

    let mut chart = ChartBuilder::on(&root)
        .caption(
            "Latency Distribution At Different Throughputs",
            ("sans-serif", 5.percent_height()),
        )
        .set_label_area_size(LabelAreaPosition::Left, 5.percent_width())
        .set_label_area_size(LabelAreaPosition::Bottom, 5.percent_height())
        .margin(1.percent())
        .build_cartesian_2d(0u32..100 + 1, 0..max_latency + 1)?;

    chart
        .configure_mesh()
        .x_desc("Percentile")
        .y_desc("Latency (ms)");

    for (index, (throughput, histogram)) in data.iter().enumerate() {
        let color = Palette99::pick(index);

        chart
            .draw_series(LineSeries::new(
                (0..100 + 1).map(|quantile| {
                    (
                        quantile,
                        histogram.value_at_quantile(quantile as f64 * 0.01),
                    )
                }),
                color.stroke_width(3),
            ))?
            .label(format!("{}", throughput))
            .legend(move |(x, y)| Rectangle::new([(x, y - 5), (x + 10, y + 5)], color.filled()));
    }

    chart
        .configure_series_labels()
        .border_style(&BLACK)
        .draw()?;

    root.present()?;

    Ok(())
}
