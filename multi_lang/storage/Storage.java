import java.io.FileWriter;
import java.io.IOException;

public class Storage {
    public static void main(String[] args) {
        System.out.println("Storing to local SQLite / File...");
        try (FileWriter file = new FileWriter("local_db.json")) {
            file.write("[]");
            System.out.println("Data persisted locally.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
