
class Program {

	public static void main(String[] args) {
		if (4 == 2)
			System.out.printf("4 == 2 (in1)\n");
		else
			System.out.printf("4 != 2 (cor1)\n");

		if (4 == 4)
			System.out.printf("4 == 4 (cor2)\n");

		if (4 == 2)
			System.out.printf("4 == 2 (in2)\n");

		int n = 2;
		int m = 10;

		if (n == 2)
			System.out.printf("n == 2 (cor3)\n");

		if (m == 3)
			System.out.printf("m == 3 (in3)\n");


		while (n == m)
		{
			System.out.printf("n == m (in3)\n");
		}


		while (n > 0)
		{
			System.out.println(n);
			n = n - 1;
		}
	}
}
