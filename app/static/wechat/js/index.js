/**
 * Created by Administrator on 2017/6/7 0007.
 */
$.ajax({
    url: "/api/is_login",
    crossDomain: true,
    type: "get",
    contentType: "application/json",
    dataType: "json",
    success: function(data) {
        if(data.code==403){
            alert('请登入后在访问');
            window.location.href="/wechat/login";
        }
    },
    error: function(err) {
        console.log(err)
    }
});
$(function(){
    var asd;
    var arr = new Array(),sum=0,test=0;
    $('#date').val('');
    var winH = $(window).height();
    var categorySpace = 10;
    //刷新页面
    // $("#tiaozhuan").click(function () {
    //     location.reload([true])
    // });
    $('.js_item').on('click', function(){
        var id = $(this).data('id');
        window.pageManager.go(id);
    });

    //改变tabbar样式
    $('.weui-tabbar__item').on('click', function () {
        $(this).addClass('weui-bar__item_on').siblings('.weui-bar__item_on').removeClass('weui-bar__item_on');
    });
    //添加图图片显示



    $gallery = $("#gallery"), $galleryImg = $("#galleryImg"),
        $uploaderInput = $("#uploaderInput"),
        $uploaderFiles = $("#uploaderFiles");

    $uploaderInput.on("change", function(e){

        var src, url = window.URL || window.webkitURL || window.mozURL, files = e.target.files;
        var len = files.length;
        for (var i=0; i < len; i++) {
            console.log($uploaderInput[0].files[i].name);
           files_name= $uploaderInput[0].files[i].name
            var file = files[i];
            if (url) {
                            src = url.createObjectURL(file);
            }else {
                            src = e.target.result;
            }
            lrz(files[i],{width:2000,fieldName:"file"}).then(function (rst) {
                test++;
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/api/uploads');
                xhr.onload = function () {
                    if (xhr.status === 200) {
                        var  data= eval('(' + xhr.responseText + ')');
                        $('#loadingToast1').css("display","none");
                        if(data.code!=403) {
                            arr.push({
                                "url": String(data.data),
                                "can_preview": true,  //如果是图片填true，word填false
                                "name":files_name,
                                "serverCode": 0, // 填0
                                "status": "success", // 填 success
                                "percentage": "100%", // 填100%
                                "id": "upfile_" + sum, // 唯一id upfile_开头
                                "error_msg": ""
                            });
                            console.log(arr);

                            var tmpl = '<li class="weui-uploader__file" id="' + sum + '" style="background-image:url(#asd)"></li>';
                            $uploaderFiles.append($(tmpl.replace('#asd', data.data[0])));
                            $uploaderInput.val("");
                            sum++;
                            console.log(sum,test)
                        }else{
                            alert("请登入后上传");
                            window.location.href="/wechat/login";
                        }
                    } else {

                    }
                };

                xhr.onerror = function () {

                };

                xhr.upload.onprogress = function (e) {
                    // 上传进度
                    // var percentComplete = ((e.loaded / e.total) || 0) * 100;
                    $("#loadingToast1").removeAttr("style");
                };
                // 添加参数
                rst.formData.append('size', rst.fileLen);

                // 触发上传
                xhr.send(rst.formData);
                return rst;
            })

                .catch(function (err) {
                    alert(err);
                })

                .always(function () {// 不管是成功失败，这里都会执行
                });

        }//for end
    });
    // $uploaderInput.on("change", function(e){
    //     test++;
    //     var t_files = this.files;
    //     var src, url = window.URL || window.webkitURL || window.mozURL, files = e.target.files;
    //     console.log(files)
    //     for (var i = 0, len = files.length; i < len; ++i) {
    //         var file = files[i];
    //         if (url) {
    //             src = url.createObjectURL(file);
    //
    //         } else {
    //             src = e.target.result;
    //         }
    //         var formData = new FormData($("#uploadForm")[0]);
    //         // alert( $uploaderInput[0].files[0].name)
    //         $.ajax({
    //             url:'/api/uploads',
    //             type:'post',
    //             // async: false,
    //             data: formData,
    //             cache: false,
    //             contentType: false,
    //             processData: false,
    //             beforeSend:function () {
    //                 $("#loadingToast1").removeAttr("style");
    //             },
    //             success:function (date){
    //                 $('#loadingToast1').css("display","none");
    //                 console.log(date)
    //                 if(date.code!=403) {
    //                     arr[sum] = {
    //                         "url": String(date.data),
    //                         "can_preview": true,  //如果是图片填true，word填false
    //                         "name": $uploaderInput[0].files[0].name,
    //                         "serverCode": 0, // 填0
    //                         "status": "success", // 填 success
    //                         "percentage": "100%", // 填100%
    //                         "id": "upfile_" + sum, // 唯一id upfile_开头
    //                         "error_msg": ""
    //                     };
    //                     console.log(arr)
    //
    //                     var tmpl = '<li class="weui-uploader__file" id="' + sum + '" style="background-image:url(#asd)"></li>';
    //                     $uploaderFiles.append($(tmpl.replace('#asd', src)));
    //                     $uploaderInput.val("");
    //                     sum++;
    //                 }else{
    //                     alert("请登入后上传")
    //                     window.location.href="/wechat/login";
    //                 }
    //             },
    //             error:function () {
    //                 alert("ajax错误");
    //             }
    //         });
    //     }
    //     // console.log(test,sum)
    // });
    //点击删除图片


    function removeByValue(arr, val) {
        for(var i=0; i<arr.length; i++) {
            if(arr[i].id == val) {
                arr.splice(i,1);
                break;
            }
        }
    }
//        var somearray = ["mon", "tue", "wed", "thur"]

    $uploaderFiles.on("click", "li", function(){
        that=this,jqthat=$(this);
        $galleryImg.attr("style", this.getAttribute("style"));
        $gallery.fadeIn(100);
        $("#tabbar").hide();

    });
    $gallery.find("a div").click(function () {
        that.remove();
        var divID = "upfile_"+jqthat.attr("id");
        removeByValue(arr,divID);
        console.log(arr);
        console.log(test,sum);
        $("#uploaderInput").val("");
        $("#shangchuang").show();
    });
    $gallery.on("click", function(){
        $gallery.fadeOut(100);
        $("#tabbar").show();
    });

    $("#submit").click(function () {
        if($('#year').val()=='请选择')
        { alert('请选择年度') }
        else if($('#Semester').val()=='请选择')
        { alert('请选择学期') }
        else if($('#date').val()=='')
        { alert('请选择考试时间') }
        else if($('#province').val()=='请选择')
        { alert('请选择所在省份') }
        else if($('#city').val()=='请选择')
        { alert('请选择所在城市') }
        else if($('#county').val()=='请选择')
        { alert('请选择所在区县') }
        else if($('#schoolclass').val()=='请选择')
        { alert('请选择学校类别') }
        else if($('#school').val()=='请选择')
        { alert('请选择所在学校') }
        else if($('#grade').val()=='请选择')
        { alert('请选择所在年级') }
        else if($('#subject').val()=='请选择')
        { alert('请选择所属科目') }
        else if($('#stage').val()=='请选择')
        { alert('请选择试卷阶段') }
        else  if($('#papuser').val()=='')
        { alert('请输入试卷名称')}
        else  if(arr=='')
        { alert('请选择图片')}
        else if(test!=sum){
            alert('请等待图片上传完成')
        }
        else {
            $.ajax({
                // url:'http://127.0.0.1:5000/api/paper/upload',
                url:'/api/paper/upload',
                type:'post',
                data:JSON.stringify({
                    "year":$("#year").val(),
                    "section":$("#Semester").val(), // FIRST_HALF 上学期 SECOND_HALF 下学期
                    "province_id":province_id,
                    "city_id":city_id ,
                    "area_id":county_id,
                    "school_id":schoolid.id,
                    "grade":$("#grade").val(),
                    "paper_types":$("#stage").val(),
                    "subject":$("#subject").val(),
                    "name":$("#papuser").val(),
                    "exam_date":$("#date").val(),
                    "attachments":arr
                }),
                // async: false,
//                data: formData,
//                cache: false,
                // contentType: false,
                // processData: false,
                dataType: "json",
                contentType: "application/json",
                traditional:true,
                beforeSend:function () {
                    $("#loadingToast2").removeAttr("style")
                    $("#submit").attr({"disabled":"disabled"});

                },
                success:function (data){
                    if(data.code==0){
                        $("#submit").removeAttr("disabled");
                        $('#formpaper')[0].reset();
                        $("#uploaderInput").val("");
                        $('li').remove();
                        arr=[];
                        alert('上传成功');
                        window.location.href="/wechat/upload";
                    }else {
                        $("#submit").removeAttr("disabled");
                        alert(data.msg)
                    }

                },
                error:function () {
                    alert("ajax错误");
                }
            });
        }
    })
});