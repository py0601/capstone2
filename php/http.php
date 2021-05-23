<?php
    $request = $_GET["age"];

	if($request=="10"){
		$temp = "age is 10";
	}
	else if($request="20"){
		$temp = "age is 20";
	}
    $response = array();

    $response["age"] = $temp;
	$response["live"]="live";
    echo json_encode($response);

?>