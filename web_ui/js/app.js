$(document).ready(function() {

	var jsondata = null
	var querystring = null

	var displayTable = function(data) {

		$('#contents').children().remove();
		if (data && data.entity.length > 0) {
			data.entity.forEach(function(e) { // each entity
				$.each(e, function(k, v) {
					trs = []
					if (v instanceof Object) { // title
						$.each(v, function(k1, v1) {
							trs.push('<tr><td><b>');
							trs.push(k + '.' + k1);
							trs.push('</b></td><td>');
							trs.push(v1);
							trs.push('</td></tr>');
						});
					}
					if (v instanceof Array) { //super_topic,type,related_item
						if (v[0].ch) {
							chs = [];
							ens = [];
							v.forEach(function(v1) {
								if (v1.ch.length > 0) {
									chs.push(v1.ch)
								}
								if (v1.en.length > 0) {
									ens.push(v1.en)
								}
							});

							trs.push('<tr><td><b>');
							trs.push(k + '.' + 'en');
							trs.push('</b></td><td>');
							trs.push(ens.join(","));
							trs.push('</td></tr>');

						} else {
							v.forEach(function(v1) {
								$.each(v1, function(k2, v2) {
									$.each(v2, function(k3, v3) {
										trs.push('<tr><td><b>');
										trs.push(k + '.' + k1 + '.' + k2 + '.' + k3);
										trs.push('</b></td><td>');
										trs.push(v3);
										trs.push('</td></tr>');
									});
								});
							});
						}
					$elem = $(trs.join(""));
				} else {
					if (typeof v == "string" && (v.indexOf("http") > - 1 || v.indexOf("https") > - 1)) {
						v = '<a href=' + v + '>' + v + '</a>';
					}
					$elem = $('<tr><td><b>' + k + '</b></td><td>' + v + '</td></tr>');
				}
				$elem.appendTo('#contents');
			});
			$('<tr class="error"><td> </td><td> </td></tr>').appendTo('#contents');
		});
	} else {
		alert("No matched entity");
	}
}

var search = function() {

	if ($("#query").val().length == 0) return;

	var spinner = new Spinner().spin();
	$("#spin").append(spinner.el);

	$.getJSON("/linking", {
		type: "query",
		query_str: $("#query").val()
	}).done(function(data) {
		spinner.stop();
		displayTable(data);
		$("#query").val("");
	});
}

$("#query").keydown(function(e) {
	if (e.which == 13) {
		e.preventDefault();
		search();
	}
});

$("#search-btn").click(function() {
	search();
});

});

