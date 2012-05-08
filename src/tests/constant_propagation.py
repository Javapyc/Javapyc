
class Program {
	public static void main(String[] args) {

		Test test = new Test();

		int a = test.throwaway(10);
		int b = 10;
		int c = 5 + b;
		int m = test.throwaway(b + c);
		a = b + c;
		c = b + a + m;

		System.out.println(a);
		System.out.println(b);
		System.out.println(c);
		System.out.println(m);

		//supported as an extension.  No assignment needed
		test.throwaway(m);
	}
}

class Test {

	public int throwaway(int n) {
		return n * n;
	}

}
