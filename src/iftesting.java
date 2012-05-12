
class IfTesting {

	public static void main(String[] args) {
        int n = 4;
        int f = 45;

        // In short: with nested ifs and any else, 
        // the else goes with the innermost if possible.

        // Baselines
        if (n < f){
            System.out.printf("Correct 1\n");
        } else {
            System.out.printf("Incorrect\n");
        }
        
        if (n < f){
            System.out.printf("Correct 2\n");
        } else 
            System.out.printf("Incorrect\n");

        
        if (n < f)
            System.out.printf("Correct 3\n");
        else {
            System.out.printf("Incorrect\n");
        }
        
        if (n < f)
            System.out.printf("Correct 4\n");
        else 
            System.out.printf("Incorrect\n");

       
        // Previously ambiguous / disallowed
        if (n < f)
            System.out.printf("Correct 5\n");

        if (n < f){
            System.out.printf("Correct 6\n");
        }

        if (n < f) 
            if (false) System.out.printf("Incorrect\n");
            else System.out.printf("Correct 7\n");

        if (n < f) 
            if (false) System.out.printf("Incorrect\n");
            else System.out.printf("Correct 8\n");
        else System.out.printf("Incorrect\n");

        
        System.out.printf("Expect empty brackets below\n[");
        if (false)
            if (false) System.out.printf("Incorrect\n");
            else System.out.printf("Incorrect\n");
        System.out.printf("]\n");

        if (true)
            if (true)
                if (true)
                    if (true)
                        System.out.printf("Correct 9\n");

        System.out.printf("Expect empty brackets below\n[");
        if (true)
            if (true)
                if (false)
                    if (true)
                        System.out.printf("Incorrect\n");
                    else System.out.printf("Incorrect\n");
        System.out.printf("]\n");

        if (true)
            if (true)
                if (false)
                    if (true)
                        System.out.printf("Incorrect\n");
                    else System.out.printf("Incorrect\n");
                else 
                    System.out.printf("Correct 10\n");


        
        
	}
}

