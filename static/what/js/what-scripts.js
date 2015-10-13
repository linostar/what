$(document).ready(function() {
	function pad(num) {
		if (num < 10)
			return "0" + num;
		else
			return num + "";
	}

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

	var timer = setInterval(function() {
		var remaining_time = parseInt($(".time-text").attr("title"));
		if (remaining_time <= 0) {
			clearInterval(timer);
		}
		else {
			var display_time = "";
			var hours;
			var minutes;
			var seconds;
			remaining_time--;
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
			$(".time-text").attr("title", remaining_time.toString());
			$(".time-text").text(display_time);
		}
	}, 1000);
});
