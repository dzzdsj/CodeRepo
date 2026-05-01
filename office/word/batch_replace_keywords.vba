Option Explicit

' =========================
' 主入口
' =========================
Sub BatchReplaceMultiKeywords()

    Dim folderPath As String
    folderPath = "C:\docs\"   ' 修改为你的目录
    
    ' ===== 替换规则（可扩展）=====
    Dim findArr As Variant
    Dim replaceArr As Variant
    
    findArr = Array("192.168.1.1", "prod-db", "nginx restart")
    replaceArr = Array("10.0.0.1", "test-db", "systemctl restart nginx")
    
    Dim fileName As String
    fileName = Dir(folderPath & "*.docx")
    
    While fileName <> ""
        
        Dim doc As Document
        Set doc = Documents.Open(folderPath & fileName)
        
        ' 执行替换
        Call ReplaceInDocument(doc, findArr, replaceArr)
        
        doc.Save
        doc.Close
        
        fileName = Dir
    Wend
    
    MsgBox "批量替换完成！"

End Sub

' =========================
' 核心替换逻辑
' =========================
Sub ReplaceInDocument(doc As Document, findArr As Variant, replaceArr As Variant)

    Dim i As Integer
    
    For i = LBound(findArr) To UBound(findArr)
        
        ' 正文
        Call ReplaceInRange(doc.Content, findArr(i), replaceArr(i))
        
        ' 页眉页脚
        Dim sec As Section
        Dim hdr As HeaderFooter
        
        For Each sec In doc.Sections
            For Each hdr In sec.Headers
                Call ReplaceInRange(hdr.Range, findArr(i), replaceArr(i))
            Next
            For Each hdr In sec.Footers
                Call ReplaceInRange(hdr.Range, findArr(i), replaceArr(i))
            Next
        Next
        
        ' 文本框（Shapes）
        Dim shp As Shape
        For Each shp In doc.Shapes
            If shp.TextFrame.HasText Then
                Call ReplaceInRange(shp.TextFrame.TextRange, findArr(i), replaceArr(i))
            End If
        Next
        
    Next

End Sub

' =========================
' 通用替换函数（核心）
' =========================
Sub ReplaceInRange(rng As Range, findText As String, replaceText As String)

    With rng.Find
        .ClearFormatting
        .Replacement.ClearFormatting
        
        .Text = findText
        .Replacement.Text = replaceText
        
        .Forward = True
        .Wrap = wdFindContinue
        
        .Format = False
        .MatchCase = False       ' 是否区分大小写
        .MatchWholeWord = False  ' 是否整词匹配
        
        .Execute Replace:=wdReplaceAll
    End With

End Sub