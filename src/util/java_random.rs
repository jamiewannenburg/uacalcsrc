//! `java.util.Random` (48-bit LCG) so seeded UACalc constructors match Java.

const MULTIPLIER: u64 = 0x5DEECE66D;
const ADDEND: u64 = 0xB;
const MASK: u64 = (1 << 48) - 1;

/// Seeded generator matching `java.util.Random` (pre-splittable, 48-bit LCG).
#[derive(Clone, Debug)]
pub struct JavaRandom {
    seed: u64,
}

impl JavaRandom {
    /// Same as `new java.util.Random(seed)`.
    pub fn new(seed: i64) -> Self {
        let mut rng = Self { seed: 0 };
        rng.set_seed(seed);
        rng
    }

    /// Same as `Random.setSeed`.
    pub fn set_seed(&mut self, seed: i64) {
        self.seed = (seed as u64 ^ MULTIPLIER) & MASK;
    }

    fn next(&mut self, bits: u32) -> i32 {
        self.seed = self.seed.wrapping_mul(MULTIPLIER).wrapping_add(ADDEND) & MASK;
        (self.seed >> (48 - bits)) as i32
    }

    /// Same as `Random.nextInt(n)` for `n > 0`.
    pub fn next_int(&mut self, n: i32) -> i32 {
        assert!(n > 0, "n must be positive");
        let n_u = n as u32;
        if n_u.is_power_of_two() {
            return (((n as i64) * (self.next(31) as i64)) >> 31) as i32;
        }
        loop {
            let bits = self.next(31);
            let val = bits % n;
            if bits.wrapping_sub(val).wrapping_add(n - 1) >= 0 {
                return val;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::JavaRandom;

    #[test]
    fn next_int_matches_java_util_random_seed_11() {
        // java.util.Random(11).nextInt(3) nine times, and nextInt(2) four times.
        let mut rng = JavaRandom::new(11);
        let ternary: Vec<i32> = (0..9).map(|_| rng.next_int(3)).collect();
        assert_eq!(ternary, vec![0, 2, 0, 0, 0, 0, 1, 2, 0]);

        let mut rng2 = JavaRandom::new(11);
        let binary: Vec<i32> = (0..4).map(|_| rng2.next_int(2)).collect();
        assert_eq!(binary, vec![1, 1, 0, 0]);
    }
}
