use std::fs;
use std::fs::File;
use std::path::PathBuf;
use std::time;

use anyhow::anyhow;
use anyhow::Context as _;
use clap::Parser;
use latency::histogram;
use walkdir::WalkDir;

#[derive(Parser)]
#[clap(about)]
enum Command {
    /// Compress raw gzipped logs into gzipped HDR histograms.
    Compress {
        #[clap(short, long)]
        output: Option<PathBuf>,

        inputs: Vec<PathBuf>,
    },

    /// Print aggregate statistics from a gzipped HDR histogram.
    Query {
        #[clap(short, long)]
        pretty: bool,

        inputs: Vec<PathBuf>,
    },

    /// Compress and report all aggregate statistics from experiment directory `input`.
    ///
    /// Only collects statistics from log files beginning with `prefix`.
    /// Optionally cache histograms under directory `output`.
    Scan {
        #[clap(short, long)]
        prefix: String,

        #[clap(short, long)]
        suffix: Option<String>,

        #[clap(short, long)]
        output: Option<PathBuf>,

        input: PathBuf,
    },

    /// Plot distributions from gzipped HDR histograms.
    Plot {
        /// Include distributions with delivery semantics `delivery`.
        #[clap(short, long)]
        delivery: String,

        /// Include distributions with maximum latency below `max_latency`.
        #[clap(short, long)]
        max_latency: Option<u64>,

        /// Exclude throughputs in `exclude`.
        #[clap(short, long, multiple = false, use_delimiter = true)]
        exclude: Vec<u32>,

        /// Include throughputs in `include`.
        #[clap(short, long, multiple = false, use_delimiter = true)]
        include: Vec<u32>,

        /// Plot using a linear Y-axis instead of logarithmic.
        #[clap(short, long)]
        linear: bool,

        /// Experiment name for plot title.
        #[clap(short, long)]
        experiment: String,

        /// Output SVG file to `output`.
        #[clap(short, long)]
        output: PathBuf,

        /// Load histograms from paths in `inputs`.
        inputs: Vec<PathBuf>,
    },
}

fn main() -> anyhow::Result<()> {
    match Command::parse() {
        Command::Compress { inputs, output } => {
            let mut histogram = histogram::new();

            for input in inputs {
                latency::compress_file(&input, &mut histogram)
                    .with_context(|| anyhow!("Compressing file: {}", input.display()))?;
            }

            histogram::write(latency::writer(output.as_deref())?, &histogram)?;
        }

        Command::Scan {
            input,
            output,
            prefix,
            suffix,
        } => {
            for entry in input.read_dir()?.filter_map(Result::ok) {
                let name = entry.file_name();
                let name = name.to_string_lossy();
                let time = entry
                    .metadata()?
                    .modified()?
                    .duration_since(time::UNIX_EPOCH)?
                    .as_secs();

                let delivery = if name.ends_with("alo") {
                    "alo"
                } else if name.ends_with("epoch") || name.ends_with("eo") {
                    "eo"
                } else {
                    panic!("Expected `alo` or `epoch`, but got: {}", name);
                };

                let (throughput, _) = name.split_once("tps_").expect("Expected `tps_` delimiter");

                let mut histogram = histogram::new();

                let cache = match output.as_deref() {
                    None => None,
                    Some(path) => {
                        let path =
                            path.join(format!("{}-{}-{}.hist.gz", delivery, throughput, time));

                        let file = File::options()
                            .read(true)
                            .create(true)
                            .write(true)
                            .open(&path)
                            .with_context(|| anyhow!("Failed to open file: {}", path.display()))?;

                        // Short-circuit with cached histogram
                        if file.metadata()?.len() > 0 {
                            let histogram = histogram::read(file)?;
                            histogram::report(&histogram, delivery, throughput, 1, false);
                            continue;
                        }

                        Some((path, file))
                    }
                };

                WalkDir::new(entry.path())
                    // Descend into `stats` (sys/boki) or `logs` (kafka) directory
                    .min_depth(2)
                    .into_iter()
                    .filter_map(Result::ok)
                    .filter(|entry| entry.file_type().is_file())
                    .filter(|entry| {
                        let name = entry.file_name().to_string_lossy();
                        name.starts_with(&prefix)
                            && suffix
                                .as_ref()
                                .map_or(true, |suffix| name.ends_with(suffix))
                    })
                    .try_for_each(|entry| {
                        latency::compress_file(entry.path(), &mut histogram).with_context(|| {
                            anyhow!("Compressing file: {}", entry.path().display())
                        })
                    })?;

                match histogram.is_empty() {
                    true => println!("{},{},x,x,x,x,x,x,x,x,x,x,x", delivery, throughput),
                    false => histogram::report(&histogram, delivery, throughput, 1, false),
                }

                match cache {
                    None => (),
                    Some((path, file)) if histogram.is_empty() => {
                        drop(file);
                        fs::remove_file(path)?;
                    }
                    Some((_, file)) => histogram::write(file, &histogram)?,
                }
            }
        }

        Command::Query { inputs, pretty } => histogram::read_all(&inputs)?.into_iter().for_each(
            |((delivery, throughput), (trials, histogram))| {
                histogram::report(&histogram, &delivery, &throughput, trials, pretty);
            },
        ),

        Command::Plot {
            inputs,
            output,
            delivery,
            max_latency,
            linear,
            experiment,
            include,
            exclude,
        } => {
            let data = histogram::read_all(&inputs)?
                .into_iter()
                .filter(|((delivery_, _), _)| delivery == *delivery_)
                .filter(|((_, throughput), _)| exclude.is_empty() || !exclude.contains(throughput))
                .filter(|((_, throughput), _)| include.is_empty() || include.contains(throughput))
                .filter(|(_, (_, histogram))| {
                    max_latency.map_or(true, |max_latency| histogram.max() <= max_latency)
                })
                .map(|((_, throughput), (_, histogram))| (throughput, histogram))
                .collect::<Vec<_>>();

            if data.is_empty() {
                return Err(anyhow!("No valid histograms found"));
            }

            latency::plot(
                &experiment,
                &delivery.to_ascii_uppercase(),
                output,
                &data,
                linear,
            )?;
        }
    }

    Ok(())
}
