use std::cmp;
use std::ops::Range;
use std::path::Path;

use hdrhistogram::Histogram;
use plotters::backend::BitMapBackend;
use plotters::backend::DrawingBackend;
use plotters::backend::SVGBackend;
use plotters::chart::ChartBuilder;
use plotters::chart::LabelAreaPosition;
use plotters::chart::SeriesLabelPosition;
use plotters::coord::combinators::IntoLogRange;
use plotters::coord::ranged1d::AsRangedCoord;
use plotters::coord::ranged1d::DefaultFormatting;
use plotters::coord::ranged1d::Ranged;
use plotters::coord::ranged1d::ValueFormatter;
use plotters::drawing::IntoDrawingArea;
use plotters::element::Rectangle;
use plotters::series::LineSeries;
use plotters::style::AsRelative as _;
use plotters::style::Color as _;
use plotters::style::Palette as _;
use plotters::style::Palette99;
use plotters::style::BLACK;
use plotters::style::WHITE;

pub fn plot<P: AsRef<Path>>(
    experiment: &str,
    delivery: &str,
    path: P,
    data: &[(String, Histogram<u32>)],
    linear: bool,
) -> anyhow::Result<()> {
    const SIZE: (u32, u32) = (1920, 1080);

    match (
        path.as_ref()
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .ends_with("png"),
        linear,
    ) {
        (true, true) => plot_internal(
            experiment,
            delivery,
            data,
            BitMapBackend::new(&path, SIZE),
            std::convert::identity,
        ),
        (true, false) => plot_internal(
            experiment,
            delivery,
            data,
            BitMapBackend::new(&path, SIZE),
            IntoLogRange::log_scale,
        ),
        (false, true) => plot_internal(
            experiment,
            delivery,
            data,
            SVGBackend::new(&path, SIZE),
            std::convert::identity,
        ),
        (false, false) => plot_internal(
            experiment,
            delivery,
            data,
            SVGBackend::new(&path, SIZE),
            IntoLogRange::log_scale,
        ),
    }
}

fn plot_internal<B, S>(
    experiment: &str,
    delivery: &str,
    data: &[(String, Histogram<u32>)],
    backend: B,
    scale: fn(Range<u64>) -> S,
) -> anyhow::Result<()>
where
    B: DrawingBackend + IntoDrawingArea,
    B::ErrorType: 'static,
    S: AsRangedCoord<Value = u64>,
    S::CoordDescType: ValueFormatter<u64> + Ranged<FormatOption = DefaultFormatting>,
    S::Value: std::fmt::Debug,
{
    let root = backend.into_drawing_area();
    root.fill(&WHITE)?;

    let (min_latency, max_latency) = data
        .iter()
        .map(|(_, histogram)| histogram)
        .filter(|histogram| !histogram.is_empty())
        .map(|histogram| (histogram.min(), histogram.max()))
        .fold((u64::MAX, 0), |(min, max), (min_, max_)| {
            (cmp::min(min, min_), cmp::max(max, max_))
        });

    let mut chart = ChartBuilder::on(&root)
        .caption(
            format!(
                "{} {} Latency Distribution At Different Throughput Per Second Per Worker",
                experiment, delivery,
            ),
            ("sans-serif", 3.percent_height()),
        )
        .set_label_area_size(LabelAreaPosition::Left, 6.percent_width())
        .set_label_area_size(LabelAreaPosition::Bottom, 6.percent_height())
        .margin(1.percent())
        .build_cartesian_2d(0u32..100 + 1, scale(min_latency..max_latency + 1))?;

    chart
        .configure_mesh()
        .x_desc("Percentile")
        .label_style(("sans-serif", 3.percent()))
        .y_desc("Latency (ms)")
        .draw()?;

    for (index, (label, histogram)) in data.iter().enumerate() {
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
            .label(label)
            .legend(move |(x, y)| Rectangle::new([(x, y - 5), (x + 20, y + 5)], color.filled()));
    }

    chart
        .configure_series_labels()
        .position(SeriesLabelPosition::UpperLeft)
        .legend_area_size(25)
        .label_font(("sans-serif", 2.percent()))
        .border_style(&BLACK)
        .draw()?;

    root.present()?;

    Ok(())
}
