package org.example;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.util.StringUtil;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DzzdsjWanted {
    public static Map<String, String> shortMap = new HashMap<>();
    public static Map<String, String> longMap = new HashMap<>();
    public static List<DiffInfo> diffInfoList = new ArrayList<>();

    public static void main(String[] args) {
        DzzdsjWanted dzzdsjWanted = new DzzdsjWanted();
        dzzdsjWanted.readExcel();
        System.out.println("===================");
        System.out.println(DzzdsjWanted.shortMap);
        System.out.println(DzzdsjWanted.longMap);
        dzzdsjWanted.compareAmount();
        System.out.println("===================");
        System.out.println(DzzdsjWanted.diffInfoList);
        dzzdsjWanted.writeExcel(DzzdsjWanted.diffInfoList);
    }

    public void compareAmount() {
        for (Map.Entry<String, String> entry : shortMap.entrySet()) {
            String shortAcct = entry.getKey();
            String shortAmount = entry.getValue();
            for (Map.Entry<String, String> longEntry : longMap.entrySet()) {
                String longAcct = longEntry.getKey();
                String longAmount = longEntry.getValue();
                if (longAcct.contains(shortAcct)) {
                    if (!shortAmount.equals(longAmount)) {
                        System.out.println("存在金额不匹配的账户数据：" + "短卡号_" + shortAcct +
                                "，金额_" + shortAmount + "，长卡号_" + longAcct + "，金额_" + longAmount);
                        DiffInfo diffInfo = new DiffInfo();
                        diffInfo.setShortAcct(shortAcct);
                        diffInfo.setShortAmount(shortAmount);
                        diffInfo.setLongAcct(longAcct);
                        diffInfo.setLongAmount(longAmount);
                        diffInfoList.add(diffInfo);
                    }
                }
            }
        }
    }


    public String getStringCellValue(Sheet sheet, int rowNum, int colNum) {
        DataFormatter formatter = new DataFormatter();
        // 获取指定行和列的单元格
        Row row = sheet.getRow(rowNum);
        if (row != null) {
            Cell cell = row.getCell(colNum);
            if (cell != null) {
                return formatter.formatCellValue(cell);
            }
        }
        return "";
    }

    /**
     * diffInfoList写入Excel
     */
    public void writeExcel(List<DiffInfo> diffInfoList) {
        // 获取JAR包所在的目录
        String jarDirectory = PathUtils.getJarDirectory();
        // 构建相对路径
        String filePath = jarDirectory + File.separator + "diffinfo.xlsx";
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("diffInfoList");
        Row headerRow = sheet.createRow(0);
        String[] headers = {"Short Account", "Short Amount", "Long Account", "Long Amount"};
        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
        }
        for (int i = 0; i < diffInfoList.size(); i++) {
            Row row = sheet.createRow(i + 1);
            row.createCell(0).setCellValue(diffInfoList.get(i).getShortAcct());
            row.createCell(1).setCellValue(diffInfoList.get(i).getShortAmount());
            row.createCell(2).setCellValue(diffInfoList.get(i).getLongAcct());
            row.createCell(3).setCellValue(diffInfoList.get(i).getLongAmount());
        }
        // 自动调整列宽
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
        // 写入文件
//        try (FileOutputStream fileOut = new FileOutputStream("/Users/dzzdsj/tmp/diffinfo.xlsx")) {
        try (FileOutputStream fileOut = new FileOutputStream(filePath)) {
            workbook.write(fileOut);
        } catch (IOException e) {
            throw new RuntimeException("Error writing Excel file", e);
        } finally {
            // 关闭工作簿
            try {
                workbook.close();
            } catch (IOException e) {
                throw new RuntimeException("Error closing workbook", e);
            }
        }

        System.out.println("Excel file has been created and written successfully.");
    }

    public void readExcel() {
        // 获取JAR包所在的目录
        String jarDirectory = PathUtils.getJarDirectory();
        // 构建相对路径
        String filePath = jarDirectory + File.separator + "workbook.xlsx";
        // 打开文件
        FileInputStream fileIn = null;
        Workbook workbook = null;
        try {
//            fileIn = new FileInputStream("/Users/dzzdsj/tmp/workbook.xlsx");
            fileIn = new FileInputStream(filePath);
            workbook = new XSSFWorkbook(fileIn);

            // 获取第一个工作表
            Sheet sheet = workbook.getSheetAt(0);
            for (int rowNum = 1; rowNum <= sheet.getLastRowNum(); rowNum++) {
                for (int colNum = 0; colNum < sheet.getRow(rowNum).getLastCellNum(); colNum++) {
                    String tmpShortAcct = getShortAcct(getStringCellValue(sheet, rowNum, 0));
                    if(StringUtil.isNotBlank(tmpShortAcct)){
                    shortMap.put(tmpShortAcct, getStringCellValue(sheet, rowNum, 1));
                    }
                    longMap.put(getStringCellValue(sheet, rowNum, 2), getStringCellValue(sheet, rowNum, 3));
                    System.out.print(getStringCellValue(sheet, rowNum, colNum) + "\t");
                }
                System.out.println();
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        } finally {
            // 关闭文件和工作簿
            try {
                if (fileIn != null) {
                    fileIn.close();
                }
                if (workbook != null) {
                    workbook.close();
                }
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    private static String getShortAcct(String input) {
        String regex = "\\((.*?)\\)";

        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(input);

        while (matcher.find()) {
            System.out.println("提取的内容: " + matcher.group(1));
            return matcher.group(1);
        }
        return input;
    }
}
