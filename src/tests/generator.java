

class Program {

	public static void main(String[] args) {
		FibGen fib = new FibGen();

		for (int n : fib.genfib(20))
			System.out.println(n);
	}
}

class FibGen {

	public int genfib(int count) {

		int n = 0;
		for (int f : this.genforever()) {
			if (n < count)
				yield f;
			else
				break;

			n = n + 1;

		}
	}

	public int genforever() {
		int i = 0;
		int j = 1;
		while (true) {
			yield i;
			j = j + i;
			i = j - i;
		}
	}

}
