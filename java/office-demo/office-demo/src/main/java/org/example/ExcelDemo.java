package org.example;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ExcelDemo {
    public static void main(String[] args) {
        List<String> column0 = new ExcelDemo().readExcelByColumn(0);
        List<String> column1 = new ExcelDemo().readExcelByColumn(1);
        System.out.println("===================");
        System.out.println(column0);
        System.out.println(column1);
    }

    public List<String> readExcelByColumn(int colNum) {
        // 打开文件
        FileInputStream fileIn = null;
        Workbook workbook = null;
        List<String> data = new ArrayList<>();
        try {
            fileIn = new FileInputStream("/Users/dzzdsj/tmp/workbook.xlsx");
            workbook = new XSSFWorkbook(fileIn);

            // 获取第一个工作表
            Sheet sheet = workbook.getSheetAt(0);
            // 使用DataFormatter来格式化单元格
            DataFormatter formatter = new DataFormatter();
            // 按指定列遍历
            System.out.print("Column " + colNum + ": ");
            for (Row row : sheet) {
                if (row.getRowNum() == 0) {
                    continue;
                }
                Cell cell = row.getCell(colNum);
                if (cell != null) {
                    switch (cell.getCellType()) {
                        case STRING:
                            System.out.print(cell.getStringCellValue() + "\t");
                            data.add(cell.getStringCellValue());
                            break;
                        case NUMERIC:
                            if (DateUtil.isCellDateFormatted(cell)) {
                                System.out.print(cell.getDateCellValue() + "\t");
                            } else {
//                                System.out.print(cell.getNumericCellValue() + "\t");
                                System.out.print(formatter.formatCellValue(cell) + "\t");
                                data.add(formatter.formatCellValue(cell));
                            }
                            break;
                        case BOOLEAN:
                            System.out.print(cell.getBooleanCellValue() + "\t");
                            break;
                        case FORMULA:
                            System.out.print(cell.getCellFormula() + "\t");
                            break;
                        default:
                            System.out.print("UNKNOWN\t");
                            break;
                    }
                } else {
                    System.out.print("\t");
                }
            }
            System.out.println();
            return data;
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
}
