$(document).ready(function() {

	var jsondata = null
	var curdata = null
	var curpage = 1;
	var filtering = false
	var querystring = null

	var prepareData = function(data) {
		data.forEach(function(d) {
			if (d.hit == "Hit") d.hit = true;
			if (d.hit == "NOT Hit") d.hit = false;
		});
		return data
	}

	var freshPage = function(data) {
		jsondata = prepareData(data);
		hitNum = 0;
		data.forEach(function(d) {
			if (d.hit) hitNum++;
		});
		$("#total-n").text(data.length);
		$("#hit-n").text(hitNum);
		var rec = (hitNum * 1.0) / data.length;
		rec = rec.toFixed(4);
		$("#hit-rec").text(rec);
		displayTable();
		curpage = 1;
	}

	var displayTable = function() {
		// Append Items to #contents here
		$('#contents').children().remove();
		displaydata = [];
		if (filtering) {
			jsondata.forEach(function(d) {
				if (d.hit) displaydata.push(d);
			});
		} else {
			displaydata = jsondata;
		}
		curdata = displaydata.slice((curpage - 1) * 8, curpage * 8);
		curdata.forEach(function(d) {

			var $elem = null;

			//			if (d.hit) {
			//				$elem = $('<tr><td><b>' + d.mention + '</b></td><td>' + d.title + '</td><td>' + d.type + '</td><td>' + d.super_topic + '</td><td>' + d.abstract + '</td><td>' + d.url + '</td><td><i class="icon-large icon-thumbs-up"></i>&nbsp<i class="icon-large icon-thumbs-down"></i></td></tr>');
			//			} else {
			//				$elem = $('<tr><td><b>' + d.mention + '</b></td><td>' + '' + '</td><td>' + '' + '</td><td>' + '' + '</td><td>' + '' + '</td><td>' + '' + '</td></tr>');
			//				$elem.addClass('error');
			//			}
			//
			if (d.hit) {
				$elem = $('<tr><td><b>' + d.mention + '</b></td><td>' + d.title + '</td><td>' + d.type + '</td><td>' + d.super_topic + '</td><td>' + d.abstract + '</td><td>' + d.url + '</td></tr>');
			} else {
				$elem = $('<tr><td><b>' + d.mention + '</b></td><td>' + '' + '</td><td>' + '' + '</td><td>' + '' + '</td><td>' + '' + '</td><td>' + '' + '</td></tr>');
				$elem.addClass('error');
			}
			$elem.appendTo('#contents');
		});
	}

	var buttonIntial = function() {

		var displayInput = function(input) {
			if (input.length > 0) {
				$("#input-show").css("display", "")
				$("#input-show span").text(input)
				querystring = input
			}
		}

		$("#filter").click(function() {
			if (jsondata) {
				if (filtering) {
					filtering = false;
					$("#filter").text("Hit Query");
					displayTable();
					curpage = 1;
				} else {
					filtering = true;
					$("#filter").text("All Query");
					displayTable();
					curpage = 1;
				}
			}
		});

		$("#author").click(function() {
			$.getJSON("/author", function(data) {
				freshPage(data);
			});
		});
		$("#term").click(function() {
			$.getJSON("/term", function(data) {
				freshPage(data);
			});
		});
		$("#paper").click(function() {
			$.getJSON("/paper", function(data) {
				freshPage(data);
			});
		});
		$("#dm-term").click(function() {
			$.getJSON("/dm-term", function(data) {
				freshPage(data);
			});
		});
	}

	var displayPager = function() {

		$('#pages').children().remove();

		$pager = $(pagination({
			cur: curpage,
			max: 15
		}));

		$pager.find('.prev-page').click(function() {
			if ($(this).hasClass('disabled')) return false;
			curpage--;
			displayPager();
			return false;
		});
		$pager.find('.num-page').click(function() {
			if ($(this).hasClass('active')) return false;
			curpage = parseInt($(this).text());
			displayPager();
			return false;
		});
		$pager.find('.next-page').click(function() {
			if ($(this).hasClass('disabled')) return false;
			curpage++;
			displayPager();
			return false;
		});

		$pager.appendTo('#pages');

		$('#contents').children().remove();
		if (jsondata) {
			displayTable();
		} else {
			//$.getJSON("/author", function(data) {
			$.getJSON("/term", function(data) {
				jsondata = data;
				freshPage(data);
			});
		}
	}
	displayPager();
	buttonIntial();
});

