
class Program {
	public static void main(String[] args) {
		Generator gen = new Generator();
		for (int i : gen.range(1, 10, 2)) {
			System.out.println(i);
		}
	}
}

class Generator {
	public int range(int start, int stop, int step) {
		while (start < stop) {
			yield start;
			start = start + step;
		}
	}
}
