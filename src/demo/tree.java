
class Main {
	public static void main(String[] args) {

		//create our tree
		Tree tree = new Tree().init();
		tree.add(10);
		tree.add(5);
		tree.add(3);
		tree.add(4);
		tree.add(15);

		//print the tree
		System.out.printf("Tree:\n%s\n\n", tree);

		//iterate over the elements in order
		System.out.printf("In order: ");
		for (int v : tree.inorder())
			System.out.printf("%d ", v);
		System.out.printf("\n\n");
	}
}

class Tree {

	Node mRoot;

	public Tree init() {
		mRoot = new LeafNode();
		return this;
	}

	public Tree add(int value) {

		if (mRoot.isLeaf()) {
			mRoot = this.createNode(value, mRoot, mRoot);

		} else {
			mRoot.add(value);
		}

		return this;
	}

	public Node createNode(int value, Node left, Node right) {
		return new ValueNode().initialize(value, left, right);
	}
	
	public Node createLeafNode(int value) {
		return new LeafNode();
	}

	public int inorder() {
		for (int v : mRoot.inorder())
			yield v;
	}

	public String toString() {
		return String.format("%s", mRoot);
	}
}

class Node {

	int mDepth;

	public boolean isLeaf() {
		return false;
	}

	public Node add(int value) {
		return this;
	}
	
	public int inorder() {
	}

	public int setDepth(int depth) {
		mDepth = depth;
		return mDepth;
	}
	
}

class LeafNode extends Node {

	public boolean isLeaf() {
		return true;
	}
	
	public Node add(int value) {
		return new ValueNode().initialize(value, this, this);
	}
	
	public String toString() {
		return "-";
	}

}

class ValueNode extends Node {

	int mValue;

	Node mLeft;
	Node mRight;

	public Node initialize(int value, Node left, Node right) {
		mValue = value;
		mLeft = left;
		mRight = right;

		return this;
	}
	
	public Node add(int value) {
		if (value != mValue) {
			if (value < mValue) {
				mLeft = mLeft.add(value);
			} else /* (value > mValue) */ {
				mRight = mRight.add(value);
			}
		}

		return this;
	}
	
	public int inorder() {
		for (int v : mLeft.inorder())
			yield v;
		yield mValue;
		for (int v : mRight.inorder())
			yield v;
	}

	public int getValue() {
		return mValue;
	}

	public String indent(String s, int depth) {
		if (depth > 0) {
			s = this.indent(String.format(" %s", s), depth-1);
		}

		return s;
	}

	public String toString() {
		mLeft.setDepth(mDepth+1);
		mRight.setDepth(mDepth+1);
		return String.format("(%d\n%s\n%s)",
				mValue,
				this.indent(String.format(" %s", mLeft), mDepth),
				this.indent(String.format(" %s", mRight), mDepth));
	}
}
