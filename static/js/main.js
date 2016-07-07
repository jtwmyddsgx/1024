

function startTime(){
					var today = new Date();
					var time = today.toLocaleString();
					document.getElementById("readTime").innerHTML=time;
					t = setTimeout("startTime()",500);
				}

function delewords(thiswords){
		
		var myForm = document.createElement("form");
		myForm.method = "post";
		myForm.action = "board";
		var dele_by_id = thiswords.id;
		var myInput = document.createElement("input");
		myInput.type = "text";
		myInput.name = "dele_by_id";
		myInput.value = dele_by_id;
		myForm.appendChild(myInput);
		document.body.appendChild(myForm);
		myForm.submit();
		document.body.removeChild(myForm);
					
}

function alertwords(thiswords){

		var myForm = document.createElement("form");
		myForm.method = "post";
		myForm.action = "board";
		var alert_by_id = thiswords.id;
		var myInput = document.createElement("input");
		myInput.type = "text";
		myInput.name = "alert_by_id";
		myInput.value = alert_by_id;
		myForm.appendChild(myInput);
		document.body.appendChild(myForm);
		myForm.submit();
		document.body.removeChild(myForm);

}

				
function addLoadEvent(func){
				var oldonload = window.onload;
				if(typeof oldonload != 'function'){
					onload = func;
				}
				else{
					window.onload = function(){
						oldonload();
						func();
					}
				}
}

function validate_required(field,alerttxt){
					with(field){
						if(value == null || value == ""){
							alert(alerttxt);
							return false;
						}
						else{
							return true;
						}
					}
				}
				
function validate_form(thisform){
					with(thisform){
						if(validate_required(username,"请输入用户名！") == false){
							username.focus();
							return false;
						}
						else if(validate_required(pwd1,"请输入密码！") == false){
							pwd1.focus();
							return false;
						}
						else if(validate_required(pwd2,"请输入密码！") == false){
							pwd2.focus();
							return false;
						}
						else if(pwd1.value != pwd2.value){

							alert("您输入的密码不一致！")
							return false;

						}
						else{
							return true;
						}
					}
				}

function replyOne(username){
    replyContent = $("#reply_content");
	oldContent = replyContent.val();
	prefix = "@" + username + " ";
	newContent = ''
	if(oldContent.length > 0){
	    if (oldContent != prefix) {
	        newContent = oldContent + "\n" + prefix;
	    }
	} else {
	    newContent = prefix
	}
	replyContent.focus();
	replyContent.val(newContent);
	moveEnd($("#reply_content"));
}

var moveEnd = function(obj){
	obj.focus();
    obj = obj.get(0);
	var len = obj.value.length;
	if (document.selection) {
		var sel = obj.createTextRange();
		sel.moveStart('character',len);
		sel.collapse();
		sel.select();
	} else if (typeof obj.selectionStart == 'number' && typeof obj.selectionEnd == 'number') {
		obj.selectionStart = obj.selectionEnd = len;
	}
}


function removeOne(removePath,thistr){
    $.ajax({
        type:"post",
        url:removePath,
        data:{theKey:thistr.id},
        success:function(response,status){
            if(status == "success"){
                alert(response),
                remoTr(thistr)
            }
            else{
                alert("任务执行失败")
            }
        }
    });
}

function remoTr(thistr){
    $(thistr).parent().parent().remove();
    $("div[class='popover-content']").text("删除成功！");
}


function removeArticle(removePath,thisDiv){
    $.ajax({
        type:"post",
        url:removePath,
        data:{theKey:thisDiv.id},
        success:function(response,status){
            if(status == "success"){
                alert(response),
                remoDiv(thisDiv)
            }
            else{
                alert("任务执行失败")
            }
        }
    });

 }


function remoDiv(thisDiv){
    $(thisDiv).parent().parent().parent().remove();
    $("div[class='popover-content']").text("删除成功！");
};


function update(update_url,thisinp){
    alert("请等待！");
    $.ajax({
        type:"post",
        url:update_url,
        data:{theKey:thisinp.id},
        success:function(response,status){
            if(status == "success"){
                alert(response)
            }
            else{
                alert("任务执行失败")
            }
        }
    });

 }