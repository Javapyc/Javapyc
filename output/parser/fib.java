
class Program {

	public static void main(String[] args) {

		//create a fib generator
		Fibonacci fib = new Fibonacci();

		int n = 15;
		while (n >= 0) {
			System.out.println(fib.fibRecursive(n));
			System.out.println(fib.fibIterative(n));
			n = n - 5;
		}

	}
}

/**
 * Calculates numbers from the Fibonacci sequence
 * using various methods
 */
class Fibonacci {

	public int fibRecursive(int n) {
		int res = n;
		if (n >= 2)
			res = this.fibRecursive(n-1) + this.fibRecursive(n-2);
		else
		{ }
		return res;
	}

	public int fibIterative(int n) {
		int i = 0;
		int j = 1;
		while (n > 0)
		{
			j = j + i;
			i = j - i;
			n = n - 1;
		}
		return i;
	}

}
