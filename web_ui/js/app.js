$(document).ready(function() {

	var jsondata = null
	var querystring = null

	var displayTable = function(data) {

		$('#contents').children().remove();
		if (data && data.entity.length > 0) {
			data.entity.forEach(function(e) {
				$.each(e, function(k, v) {
					if (typeof v == "object") {
						trs = []
						$.each(v, function(k1, v1) {
							trs.push('<tr><td><b>');
							trs.push(k + '.' + k1);
							trs.push('</b></td><td>');
							trs.push(v1);
							trs.push('</td></tr>');
						})
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

	$("#search-btn").click(function() {
		if ($("#query").val().length == 0) return;

		$.getJSON("/linking", {
			type: "query",
			query_str: $("#query").val()
		}).done(function(data) {
			displayTable(data);
		});
	});

});

