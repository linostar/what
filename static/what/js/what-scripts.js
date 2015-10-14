$(document).ready(function() {
	function pad(num) {
		if (num < 10)
			return "0" + num;
		else
			return num + "";
	}

	$("#navbar-rules").click(function() {
		var rules = $("#rules-hidden").attr("value") || "No rules.";
		bootbox.dialog({
			title: "Rules",
			message: rules,
			buttons: {
				main: {
					label: "Close",
					className: "btn-primary"
				}
			}
		});
	});

	$(".answers").click(function() {
		if ($(this).hasClass("yellow")) {
			$(this).removeClass("yellow");
			$(this).parent().find(".chosen-answer").val("");
		} 
		else {
			var question_id = ($(this).parent().attr("id")).substring(8);
			var answer_id = ($(this).attr("id")).substring(6);
			$(".answer-q" + question_id).removeClass("yellow");
			$(this).addClass("yellow");
			$(this).parent().find(".chosen-answer").val(answer_id);
		}		
	});

	$("#submit-button").click(function() {
		$("#form-submit").submit();
	});

	var timer = setInterval(function() {
		var ending_soon = false;
		var remaining_time = parseInt($("#remaining-time-hidden").attr("value"));
		if (remaining_time <= 0) {
			clearInterval(timer);
			$("#form-submit").submit();
		}
		else {
			var display_time = "";
			var hours;
			var minutes;
			var seconds;
			remaining_time--;
			if (remaining_time <= 30)
				ending_soon = true;
			else
				ending_soon = false;
			if (ending_soon) {
				$(".circle").css("background", "linear-gradient(135deg, #f85032 0%,#f16f5c 50%,#f6290c 51%,#f02f17 71%,#e73827 100%)");
				$(".circle-border").css("border", "3px solid #882222");
			}
			if (remaining_time < 60) {
				seconds = remaining_time.toString();
				display_time = seconds;
			}
			else if (remaining_time < 3600) {
				minutes = Math.floor(remaining_time / 60);
				seconds = remaining_time % 60;
				display_time = pad(minutes) + ":" + pad(seconds);
			}
			else {
				hours = Math.floor(remaining_time / 3600);
				minutes = Math.floor((remaining_time - hours * 3600) / 60);
				seconds = remaining_time % 60;
				display_time = hours + ":" + pad(minutes) + ":" + pad(seconds);
			}
			$("#remaining-time-hidden").val(remaining_time.toString());
			$(".time-text").text(display_time);
		}
	}, 1000);
});
