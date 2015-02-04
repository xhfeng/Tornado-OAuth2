Welcome to the Tornado-OAuth2 wiki!

### 项目简介

基于 `Tornado` 和 `oauthlib` 实现的 `OAuth2` 认证授权服务端

OAuth 2.0定义了四种授权方式。

* 授权码模式（authorization code）
* 简化模式（implicit）
* 密码模式（resource owner password credentials）
* 客户端模式（client credentials）

该项目 `0.0.1` 实现 `密码模式`

一 [项目简介](https://github.com/rsj217/Tornado-OAuth2/wiki/%E4%B8%80-%E9%A1%B9%E7%9B%AE%E7%AE%80%E4%BB%8B)

二 [密码模式](https://github.com/rsj217/Tornado-OAuth2/wiki/%E4%BA%8C-%E5%AF%86%E7%A0%81%E6%A8%A1%E5%BC%8F-Resource-Owner-Password-Credentials-Grant)

该项目 0.0.1 实现 密码模式

密码模式（Resource Owner Password Credentials Grant）中，用户向客户端提供自己的用户名和密码。客户端使用这些信息，向"服务商提供商"索要授权。
在这种模式中，用户必须把自己的密码给客户端，但是客户端不得储存密码。这通常用在用户对客户端高度信任的情况下，比如客户端是操作系统的一部分，或者由一个著名公司出品。通常提供给自己的客户端使用。

流程图

    +----------+
    | Resource |
    |  Owner   |
    |          |
    +----------+
         v
         |    Resource Owner
        (A) Password Credentials
         |
         v
    +---------+                                  +---------------+
    |         |>--(B)---- Resource Owner ------->|               |
    |         |         Password Credentials     | Authorization |
    | Client  |                                  |     Server    |
    |         |<--(C)---- Access Token ---------<|               |
    |         |    (w/ Optional Refresh Token)   |               |
    +---------+                                  +---------------+
    
           Figure 5: Resource Owner Password Credentials Flow

大致过程：

* （A）用户向客户端提供用户名和密码。
* （B）客户端将用户名和密码发给认证服务器，向后者请求令牌。
* （C）认证服务器确认无误后，向客户端提供访问令牌。

B步骤中，客户端发出的HTTP请求，包含以下参数：

    grant_type：表示授权类型，此处的值固定为"password"，必选项。
    username：表示用户名，必选项。
    password：表示用户的密码，必选项。
    scope：表示权限范围，可选项。
    
一个例子。

     POST /token HTTP/1.1
     Host: server.example.com
     Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW
     Content-Type: application/x-www-form-urlencoded

     grant_type=password&username=username&password=password

C步骤中，认证服务器向客户端发送访问令牌，下面是一个例子。

     HTTP/1.1 200 OK
     Content-Type: application/json;charset=UTF-8
     Cache-Control: no-store
     Pragma: no-cache

     {
        'access_token': 'uEtBIw1r81BM28K2CZWG9i13ULoRkw', 
        'token_type': 'Bearer', 
        'expires_in': 3600, 
        'refresh_token': 'OUJpOvXyo46l7BSleutLhbPNFzrXtz', 
        'scope': 'common'
     }

其中的 headers 认证 client 的合法性

basic 方式

    client_id: s6BhdRkqt3
    client_secret: 7Fjfp0ZBr1KtDRbnfVdmIw

第一步：把ID和Secret连起来，中间用冒号:分开，变成这样：

    s6BhdRkqt3:7Fjfp0ZBr1KtDRbnfVdmIw
    
第二步：用base64 编码，变成这样

    czZCaGRSa3F0Mzo3RmpmcDBaQnIxS3REUmJuZlZkbUl3

第三步：加上 Basic 前缀
    
    Basic czZCaGRSa3F0Mzo3RmpmcDBaQnIxS3REUmJuZlZkbUl3
    
第四步：最后得到的HTTP Auth 的header 就是：

    Authorization: Basic czZCaGRSa3F0Mzo3RmpmcDBaQnIxS3REUmJuZlZkbUl3