# -*- coding:utf-8 -*-


from CCPRestSDK import REST
import ConfigParser
import logging


# 1.免费开发测试需要使用"控制台首页"中，开发者主账户相关信息，如主账号、应用ID等。
#
# 2.免费开发测试使用的模板ID为1，形式为：【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入。

#主帐号
accountSid= '8a216da86150f04301616598d68005ce'

#主帐号Token
accountToken= '3fc8ca5519044d80953b2573a938a2ae'

#应用Id
appId='8aaf07086150ec5001616a1381750796'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口
serverPort='8883'

#REST版本号
softVersion='2013-12-26'
# # 主帐号
# accountSid= '8aaf07085f9eb021015fb58c56d906e8'
#
# # 主帐号Token
# accountToken= 'e21ca96da61c49ee97e0fdf1ba47de5a'
#
# # 应用Id
# appId='8aaf07085f9eb021015fb58c574106ef'
#
# # 请求地址，格式如下，不需要写http://
# serverIP='app.cloopen.com'
#
# # 请求端口
# serverPort='8883'
#
# # REST版本号
# softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：['12','34']，如不需替换请填 ''
  # @param $tempId 模板Id
#
class CCP(object):
    # 单例模式
    def __new__(cls, *args, **kwargs):
        # 判断系统是否有instance的值
        if not hasattr(cls,'instance'):
            cls.instance = super(CCP,cls).__new__(cls)

            # 初始化REST SDK 封装鉴权
            cls.instance.rest = REST(serverIP, serverPort, softVersion)
            cls.instance.rest.setAccount(accountSid, accountToken)
            cls.instance.rest.setAppId(appId)
        # 返回
        return cls.instance

    def send_template_sms(self,to,datas,tempId):

        try:
            result = self.instance.rest.sendTemplateSMS(to, datas, tempId)
        except Exception as e:
            logging.error(e)
            raise e
        return result.get('statusCode')

    # def sendTemplateSMS(to,datas,tempId):
    #
    #
    #     # #初始化REST SDK
    #     # rest = REST(serverIP,serverPort,softVersion)
    #     # rest.setAccount(accountSid,accountToken)
    #     # rest.setAppId(appId)
    #
    #     result = rest.sendTemplateSMS(to,datas,tempId)
    #     for k,v in result.iteritems():
    #
    #         if k=='templateSMS' :
    #                 for k,s in v.iteritems():
    #                     print '%s:%s' % (k, s)
    #         else:
    #             print '%s:%s' % (k, v)
    
   
#sendTemplateSMS(手机号码,内容数据,模板Id)
if __name__ == '__main__':
    # sendTemplateSMS(17710928803,['惠主播,我没钱了',5],1)
    cpp = CCP()
    cpp.send_template_sms(17710928803,['中国人',5],1)