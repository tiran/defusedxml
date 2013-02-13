#!/usr/bin/php
<?php

// $options = 0;
// $options = LIBXML_NONET;
$options = LIBXML_NOENT;

$xml = simplexml_load_file($argv[1], "SimpleXMLElement", $options);
$data = (string)$xml;
echo strlen($data);
echo $data;
?>

