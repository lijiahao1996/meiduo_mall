from ronglian_sms_sdk import SmsSDK

accId = '2c94811c9860a9c4019ac5ab8beb5ac1'
accToken = 'e0b639b11fc64f33b9bc1c8cd6c0814f'
appId = '2c94811c9860a9c4019ac5ab8cab5ac8'

def send_message():
    # 初始化 SDK
    sdk = SmsSDK(accId, accToken, appId)

    tid = '1'  # 模板ID
    mobile = '13021020077'  # 手机号（多个号码用逗号隔开）
    datas = ('8888', '20')   # 模板变量

    # 调用接口
    resp = sdk.sendMessage(tid, mobile, datas)

    print("返回结果：", resp)

if __name__ == "__main__":
    send_message()




