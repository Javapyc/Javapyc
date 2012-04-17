
class Program {
	public static void main(String[] args) {

		Test test = new Test();

		int n = test.throwaway(10);
		n = test.throwaway(n);
		//supported as an extension.  No assignment needed
		test.throwaway(n);
	}
}

class Test {

	public int throwaway(int n) {
		return n * n;
	}

}
