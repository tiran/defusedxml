#!/usr/bin/php
<?php
$xml = simplexml_load_file($argv[1]);
$data = (string)$xml;
echo strlen($data);
echo $data;
?>

