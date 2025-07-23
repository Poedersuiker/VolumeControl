/**
 * Basic Parameter Description:
 *      @local Whether internationalized
 *      @back Independently determine the timing of echoing
 *      @dom Save required document elements
 *      @propEvent Software callback event - Strategy mode
 * ==================================================>
 */
const $local = false, $back = false,
    $dom = {
        main: $('.sdpi-wrapper'),
    },
    $propEvent = {
        didReceiveSettings(data) {
            console.log("didReceiveSettings",data);
            $settings.test = 121;
            $websocket.sendToPlugin({ PropertyInspector: 121});
            $websocket.setGlobalSettings({ PropertyInspector: 165415 });
        },
        sendToPropertyInspector(data) { 
            console.log("sendToPropertyInspector",data);
        },
        didReceiveGlobalSettings(data) {
            console.log("didReceiveGlobalSettings",data);
        },
    };