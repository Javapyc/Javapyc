public HashSet readInClustering(String clusterFilename)
{
	// Hashset doesn't allow duplicates. Do we really want this?
	HashSet ret = new HashSet();
	BasicDiskTable clusters = new BasicDiskTable(new File(clusterFilename));
	clusters.open();
	String [] line = clusters.readLine();
	HashSet cluster = new HashSet();
	while(line!=null) {
		if(line.length>0 && line[0].trim().length()>0) {
			//System.out.println(GeneralUtility.join(line, " :: "));
			totalElements++;
			/** Do this block when clustering
			// System.out.println(line[0]);*/
			cluster.add(line[0]);	
		}
	}
}
