
class Program {
	public static void main(String[] args) {
		System.out.printf("Printf test cases\n"
				  "\n");

		int a = 40;
		System.out.printf("a = %d\n", a);
		System.out.printf("a + 2 = %d\n", a + 2);
		System.out.printf("%d + 2 = %d\n\n", a, a + 2);

		int b = 80;
		System.out.printf("b = %d\n", b);
		System.out.printf("a < b = %b\n", a < b);
		System.out.printf("%d < %d = %b\n\n", a, b, a < b);
		
		System.out.printf("a > b = %b\n"
		                  "%d > %d = %b\n"
				  "\n", a > b, a, b, a > b);


		System.out.printf("Other tests:\n");
		System.out.printf("[1;34mBlue Text[0m\n");
		System.out.printf("Backslash: \\\n");
		System.out.printf("Quote:     \"\n");
	}
}

