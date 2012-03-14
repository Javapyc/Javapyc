
class Program {

	public static void main(String[] args) {

		//create a fib generator
		Fibonacci fib = new Fibonacci();

		int n = 15;
		while (n) {
			System.out.println(fib.fib_recursive(n));
			System.out.println(fib.fib_iterative(n));
			n = n - 5;
		}

	}
}

/**
 * Calculates numbers from the Fibonacci sequence
 * using various methods
 */
class Fibonacci {

	public int fib_recursive(int n) {
		int res = n;
		if (n >= 2)
			res = this.fib_recursive(n-1) + this.fib_recursive(n-2);
		return res;
	}

	public int fib_iterative(int n) {
		int i = 0;
		int j = 1;
		while (n)
		{
			j = j + i;
			i = j - i;
			n = n - 1;
		}
		return j;
	}

}
