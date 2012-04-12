
class Main {
	public static void main(String[] args) {
		Rational frac = new Rational();
		Scalar s = new Scalar();

		//throwaway return values
		int i = 0;
		boolean b = false;

		b = frac.setNumerator(1);
		b = frac.setDenominator(2);
		i = s.setValue(2);

		Rational scaled = frac.scale(s);

		System.out.println(scaled.getNumerator());
		System.out.println(scaled.getDenominator());

		frac = frac.scale(s).multiply(frac);
		System.out.println(frac.getNumerator());
		System.out.println(frac.getDenominator());
	}
}

class Object {
	public int hashCode() {
		return -1;
	}
}

class Scalar extends Object {
	int value;

	public int setValue(int val) {
		value = val;
		return value;
	}
	
	public int getValue() {
		return value;
	}

	public int hashCode() {
		return this.getValue();
	}
}

class Rational extends Object {

	int numerator;
	int denominator;

	/**
	 * Removes common factors from numerator and denominator
	 *
	 * @return true if a reduction was made; false otherwise
	 */
	public boolean reduce() {
		//TODO implement reduce (not really)
		return false;
	}

	public int getNumerator() {
		return numerator;
	}

	public int getDenominator() {
		return denominator;
	}
	
	public boolean setNumerator(int val) {
		numerator = val;
		return this.reduce();
	}
	
	public boolean setDenominator(int val) {
		denominator = val;
		return this.reduce();
	}

	public int round() {
		return numerator / denominator;
	}

	public boolean isFractional() {
		return numerator < denominator;
	}
	
	public Rational multiply(Rational o) {
		Rational res = new Rational();

		boolean b = false;

		b = res.setNumerator(this.getNumerator() * o.getNumerator());
		b = res.setDenominator(this.getDenominator() * o.getDenominator());

		return res;
	}

	public Rational scale(Scalar scalar) {
		Rational res = new Rational();
		int scale = scalar.getValue();

		boolean b = false;

		b = res.setNumerator(numerator * scale);
		b = res.setDenominator(denominator * scale);

		return res;
	}
}

