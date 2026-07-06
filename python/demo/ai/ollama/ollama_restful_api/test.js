
function escapeHTML(str) {
    return str.replace(/[&<>"' \t\n\r\f\v]/g, function (match) {
        const escapeMap = {
            '&': '&amp;',  // 修正 & 的转义
            '<': '&lt;',   // 修正 < 的转义
            '>': '&gt;',   // 修正 > 的转义
            '"': '&quot;',
            "'": '&#39;',
            ' ': '&nbsp;',
            '\t': '&nbsp;&nbsp;&nbsp;&nbsp;', // 将制表符替换为四个空格，更直观
            '\n': '<br/>',  // 将换行符替换为 HTML 换行标签 <br/>
            '\r': '',       // 忽略回车符（通常与 \n 一起使用）
            '\f': '&#12;',  // 换页符
            '\v': '&#11;'   // 垂直制表符
        };
        return escapeMap[match];
    });
}

console.log(escapeHTML("<think>")); // 输出 &lt;think&gt;
console.log(escapeHTML("This is a test with a\nnewline & a \"quote\".")); //输出 This&nbsp;is&nbsp;a&nbsp;test&nbsp;with&nbsp;a<br/>newline&nbsp;&amp;&nbsp;a&nbsp;&quot;quote&quot;.
console.log(escapeHTML("Tab test:\tHello")); //输出 Tab&nbsp;test:&nbsp;&nbsp;&nbsp;&nbsp;Hello
console.log(escapeHTML("Multiple   spaces")); // 输出 Multiple&nbsp;&nbsp;&nbsp;spaces