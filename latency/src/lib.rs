mod compress;
pub mod histogram;
mod plot;

pub use compress::compress_file;
pub use plot::plot;

use std::fs::File;
use std::io;
use std::io::Read;
use std::io::Write;
use std::path::Path;

use anyhow::anyhow;
use anyhow::Context as _;

enum Or<L, R> {
    L(L),
    R(R),
}

pub fn reader(path: Option<&Path>) -> anyhow::Result<impl Read> {
    match path {
        None => (),
        Some(path) if path == Path::new("-") => (),
        Some(path) => {
            return File::open(path)
                .map(Or::R)
                .with_context(|| anyhow!("Failed to open file: {}", path.display()))
        }
    }

    Ok(Or::L(io::stdin().lock()))
}

pub fn writer(path: Option<&Path>) -> anyhow::Result<impl Write> {
    match path {
        None => (),
        Some(path) if path == Path::new("-") => (),
        Some(path) => {
            return File::options()
                .create_new(true)
                .write(true)
                .open(path)
                .map(Or::R)
                .with_context(|| anyhow!("Failed to open file: {}", path.display()));
        }
    }

    Ok(Or::L(io::stdout().lock()))
}

impl<L: Read, R: Read> Read for Or<L, R> {
    fn read(&mut self, buffer: &mut [u8]) -> io::Result<usize> {
        match self {
            Or::L(left) => left.read(buffer),
            Or::R(right) => right.read(buffer),
        }
    }
}

impl<L: Write, R: Write> Write for Or<L, R> {
    fn write(&mut self, buffer: &[u8]) -> io::Result<usize> {
        match self {
            Or::L(left) => left.write(buffer),
            Or::R(right) => right.write(buffer),
        }
    }

    fn flush(&mut self) -> io::Result<()> {
        match self {
            Or::L(left) => left.flush(),
            Or::R(right) => right.flush(),
        }
    }
}
