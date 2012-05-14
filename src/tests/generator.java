

class Program {

	public static void main(String[] args) {
		FibGen fib = new FibGen();

	}
}

class FibGen {

	public int genfib(int count) {
		int n = 0;
		int i = 0;
		int j = 1;
		while (n < count) {
			yield i;
			j = j + i;
			i = j - i;
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
