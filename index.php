<?php

$httpResponse = array();
error_reporting(E_ALL);
ini_set('display_errors', 1);
//
function verifyPostData() {
    $result = false;
    if(isset($_POST["chatRoomName"]) && isset($_POST["nickname"]) && isset($_POST["command"])) {
        if(strlen($_POST["chatRoomName"]) > 0 && strlen($_POST["nickname"]) && strlen($_POST["command"]) > 0) {
                $result = true;
            }
        }
    return $result;
}
if(verifyPostData()) {
    if($_POST["command"] == "initChatSession") {
        if(!file_exists($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"])) {
            if(mkdir($_POST["chatRoomName"], 0777)) {
                $httpResponse["status"] = "success";
            } else {
                $httpResponse["status"] = "fail";
            }
        } else if(file_exists($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"])) {
            $httpResponse["status"] = "success";
        }

    } else if($_POST["command"] == "createChatEntryInsideChatRoom") {
        $file = fopen($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $_POST["nickname"],"w+");
        if($file) {
            fclose($file);
            $httpResponse["status"] = "success";

        } else {
            $httpResponse["status"] = "fail";
        }
    } else if($_POST["command"] == "sendChatMessage"){
        $file = fopen($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $_POST["nickname"],"r+");
        if($file) {
             $fileContent = NULL;
            if(filesize($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $_POST["nickname"]) > 0) {
             $fileContent = fread($file, filesize($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $_POST["nickname"]));   
            }
            $fileContent .= "\n";
             $fileContent .= $_POST["chatMessageContent"];
            fwrite($file, $fileContent);
            fclose($file);
            $httpResponse["status"] = "success";

        } else {
            $httpResponse["status"] = "fail";
        }
    } else if($_POST["command"] == "receiveChatMessage") {
        $otherNickname;
        $directoryContent = scandir($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/");
        for($x = 0; $x < count($directoryContent); $x++) {
            if($directoryContent[$x] != ".." && $directoryContent[$x] != "." && $directoryContent[$x] != $_POST["nickname"]) {
                $otherNickname = $directoryContent[$x];
            }
        }

        $file = fopen($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $otherNickname, "r+");
        if($file){
            $chatMessageContent;
            if(filesize($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $otherNickname) > 0) {
                $chatMessageContent = fread($file, filesize($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $otherNickname));
                fclose($file);
                $file = fopen($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/" . $otherNickname, "w+");
                $httpResponse["status"] = "success";
                $httpResponse["receivedChatMessage"] = $chatMessageContent;
                $httpResponse["senderNickname"] = $otherNickname;
            } else {
                $httpResponse["status"] = "fail";
            }
        }
        fclose($file);
    }
    else if($_POST["command"] == "getChatRoomPeopleCount") {

        $chatRoomPeopleCount = 0;
        if(file_exists($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/")) {
            $directoryContent = scandir($_SERVER["DOCUMENT_ROOT"] . "/" . $_POST["chatRoomName"] . "/");
            for($x = 0; $x < count($directoryContent); $x++) {
                if($directoryContent[$x] != ".." && $directoryContent[$x] != ".") {
                    $chatRoomPeopleCount++;
                }
            }
        }
        $httpResponse["chatRoomPeopleCount"] = $chatRoomPeopleCount;
    }


} else {
    echo "error_invalid_request";
}

echo json_encode($httpResponse);
?>