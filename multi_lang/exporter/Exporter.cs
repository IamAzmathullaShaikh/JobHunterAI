using System;
using System.IO;

class Exporter {
    static void Main() {
        Console.WriteLine("Generating CSV export...");
        File.WriteAllText("export.csv", "Title,Company,Score\nBackend Engineer,TechCorp,80");
        Console.WriteLine("CSV generated locally.");
    }
}
