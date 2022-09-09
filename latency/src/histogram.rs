use std::collections::BTreeMap;
use std::fmt::Display;
use std::io::Read;
use std::io::Write;
use std::path::PathBuf;

use anyhow::Context as _;
use hdrhistogram::serialization::Deserializer;
use hdrhistogram::serialization::Serializer as _;
use hdrhistogram::serialization::V2Serializer;
use hdrhistogram::Histogram;
use walkdir::WalkDir;

pub fn new() -> Histogram<u32> {
    // Note: maximum latency should definitely be below 15 minutes
    Histogram::new_with_max(1_000 * 60 * 15, 3).expect("Expected valid histogram configuration")
}

#[allow(clippy::type_complexity)]
pub fn read_all(
    inputs: &[PathBuf],
) -> anyhow::Result<BTreeMap<(String, u32), (Vec<String>, Histogram<u32>)>> {
    let mut histograms = BTreeMap::default();

    for entry in inputs
        .iter()
        .flat_map(|input| WalkDir::new(input).max_depth(1))
        .filter_map(Result::ok)
        .filter(|entry| entry.file_type().is_file())
    {
        let (delivery, throughput) = match entry
            .file_name()
            .to_string_lossy()
            .split_once('-')
            .and_then(|(delivery, next)| {
                let (throughput, _) = next.split_once('-')?;
                Some((delivery.to_owned(), throughput.parse::<u32>().ok()?))
            }) {
            Some((delivery, throughput)) => (delivery, throughput),
            None => {
                eprintln!(
                    "Ignoring unrecognized file name: {}",
                    entry.path().display()
                );
                continue;
            }
        };

        let partial = read(crate::reader(Some(entry.path()))?)?;

        if partial.is_empty() {
            eprintln!("Ignoring empty histogram: {}", entry.path().display());
            continue;
        }

        let (trials, total) = histograms
            .entry((delivery, throughput))
            .or_insert_with(|| (Vec::new(), new()));

        trials.push(entry.file_name().to_string_lossy().into_owned());
        *total += partial;
    }

    Ok(histograms)
}

pub fn read<R: Read>(reader: R) -> anyhow::Result<Histogram<u32>> {
    let mut reader = flate2::read::GzDecoder::new(reader);
    let histogram = Deserializer::new()
        .deserialize(&mut reader)
        .context("Failed to deserialize histogram")?;
    Ok(histogram)
}

pub fn write<W: Write>(writer: W, histogram: &Histogram<u32>) -> anyhow::Result<()> {
    let mut writer = flate2::write::GzEncoder::new(writer, flate2::Compression::default());
    V2Serializer::new()
        .serialize(histogram, &mut writer)
        .context("Failed to serialize histogram")?;
    Ok(())
}

pub fn report<S>(
    histogram: &Histogram<u32>,
    delivery: &str,
    throughput: impl Display,
    trials: &[S],
    pretty: bool,
) where
    S: AsRef<str>,
{
    if pretty {
        println!("delivery: {}", delivery);
        println!("throughput/sec/worker: {}", throughput);
        println!("\ttrials: {}", trials.len());
        println!("\tpoints: {}", histogram.len());
        println!("\tavg (ms): {:.03}", histogram.mean());
        println!("\tstd (ms): {:.03}", histogram.stdev());
        println!("\tmin (ms): {}", histogram.min());
        println!("\tp25 (ms): {}", histogram.value_at_quantile(0.25));
        println!("\tp50 (ms): {}", histogram.value_at_quantile(0.50));
        println!("\tp75 (ms): {}", histogram.value_at_quantile(0.75));
        println!("\tp90 (ms): {}", histogram.value_at_quantile(0.90));
        println!("\tp99 (ms): {}", histogram.value_at_quantile(0.99));
        println!("\tmax (ms): {}", histogram.max());
        println!();
    } else {
        print!("{},{},", delivery, throughput,);

        match trials {
            [trial] => print!("{},", trial.as_ref()),
            _ => print!("{},", trials.len()),
        }

        println!(
            "{},{:.03},{:.03},{},{},{},{},{},{},{}",
            histogram.len(),
            histogram.mean(),
            histogram.stdev(),
            histogram.min(),
            histogram.value_at_quantile(0.25),
            histogram.value_at_quantile(0.50),
            histogram.value_at_quantile(0.75),
            histogram.value_at_quantile(0.90),
            histogram.value_at_quantile(0.99),
            histogram.max(),
        );
    }
}
