
class Program {
	public static void main(String[] args) {
		System.out.printf("Printf test cases");
		System.out.printf("");

		int a = 40;
		System.out.printf("a = %d", a);
		System.out.printf("a + 2 = %d", a + 2);
		System.out.printf("%d + 2 = %d", a, a + 2);
		System.out.printf("");


		int b = 80;
		System.out.printf("b = %d", b);
		System.out.printf("a < b = %b", a < b);
		System.out.printf("%d < %d = %b", a, b, a < b);
		System.out.printf("");
		
		System.out.printf("a > b = %b", a > b);
		System.out.printf("%d > %d = %b", a, b, a > b);
	}
}

