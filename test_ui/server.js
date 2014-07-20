var express = require('express')
var app = express();
var jade = require('jade');
var fs = require('fs');
var path = require('path');
var csvtojson = require('csvtojson');

var getCsv = function(filename, res) {

	var csvConverter = new csvtojson.core.Converter();

	csvConverter.on("end_parsed", function(jsonObj) {
		res.send(jsonObj);
	});

	fs.createReadStream(filename).pipe(csvConverter);
}

var page = jade.renderFile('index.jade');
app.get('/', function(req, res) {

	res.send(page);
});

app.get('/author', function(req, res) {

	var csvFile = "../test/new_author_hit.csv";
	getCsv(csvFile, res);
});

app.get('/term', function(req, res) {
	var csvFile = "../test/new_interest_hit.csv";
	getCsv(csvFile, res);

});

app.get('/paper', function(req, res) {
	var csvFile = "../test/new_pub_hit.csv";
	getCsv(csvFile, res);
});

app.use(express.static(path.join(__dirname, './')));
app.listen(3000);

