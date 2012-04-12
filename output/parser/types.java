
class Main {
	public static void main(String[] args) {

		DoubleMultiplier mult = new DoubleMultiplier();

		int i = 0;
		boolean b = false;

		b = mult.setValue(1);
		System.out.println(mult.scale(10)); /* 10 */
		System.out.println(mult.doublescale(1)); /* 20 */

		Collatz c = new Collatz();
		System.out.println(c.steps(21)); /* 7 */
	
		Params p = new Params();
		System.out.println(p.random());    /*  4 */
		System.out.println(p.add1(10));    /* 11 */
		System.out.println(p.addX(10, 5)); /* 15 */
		System.out.println(p.sum(1,2,3));  /*  6 */
	}
}

class Multiplier {

	int value;

	public boolean setValue(int val) {
		value = val;
		return true;
	}

	public int scale(int n) {
		value = value * n;
		return value;
	}
}

class DoubleMultiplier extends Multiplier {

	public int doublescale(int n) {
		value = value * 2 * n;
		return value;
	}
}

class Collatz {
	public int steps(int n) {
		int res = 0;
		if (n > 1) {
			while (n != 1) {
				if (n / 2 * 2 == n) {
					/* even */
					n = n / 2;

				} else {
					/* odd */
					n = 3 * n + 1;
				}
				res = res + 1;
			}

		} else {
			res = -1;
		}

		return res;
	}
}

class Params {

	public int random() {
		return 4;
	}
	
	public int add1(int n) {
		return n + 1;
	}
	
	public int addX(int n, int x) {
		return n + x;
	}
	
	public int sum(int a, int b, int c) {
		return a + b + c;
	}
}

