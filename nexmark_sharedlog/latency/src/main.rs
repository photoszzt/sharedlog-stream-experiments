use std::fs;
use std::io::Write;
use std::iter;
use std::path::PathBuf;

struct Arguments {
    inputs: Vec<PathBuf>,
    output: PathBuf,
}

fn main() -> anyhow::Result<()> {
    let mut arguments = pico_args::Arguments::from_env();

    let arguments = Arguments {
        output: arguments.value_from_str("--output")?,
        inputs: iter::from_fn(|| arguments.opt_free_from_str().transpose())
            .collect::<Result<Vec<_>, _>>()?,
    };

    let mut output = fs::File::options()
        .write(true)
        .create_new(true)
        .open(arguments.output)
        .map(|file| flate2::write::GzEncoder::new(file, flate2::Compression::default()))?;

    for input in arguments.inputs {
        fs::File::open(&input)
            .map(flate2::read::GzDecoder::new)
            // Shouldn't need to parse entire JSON object here
            .map(serde_json::from_reader::<_, serde_json::Value>)??
            .get_mut("Latencies")
            .expect("Expected 'Latencies' key in metrics JSON")
            .get_mut("eventTimeLatency_sink")
            .expect("Expected 'eventTimeLatency_sink' key in metrics JSON")
            .as_array_mut()
            .map(|array| array.drain(..))
            .expect("Expected .Latencies.eventTimeLatency_sink to be an array")
            .map(|time| time.as_u64().expect("Expected latencies to be integers"))
            .map(|time| u16::try_from(time).expect("Expected latencies to be below u16::MAX"))
            .try_for_each(|time| output.write_all(time.to_le_bytes().as_slice()))?;
    }

    Ok(())
}
