rule QasabaGoAgent
{
	meta:
		author = "hex-a-dec"
		description = "Qasaba Go agent detection rule"
	strings:
		$bytes4 = { 63 7279 7074 6f2f 7835 3039 }
		$bytes2 = { 2f 6167 656e 7473 2f }
	condition:
	$bytes2 and $bytes4
}
