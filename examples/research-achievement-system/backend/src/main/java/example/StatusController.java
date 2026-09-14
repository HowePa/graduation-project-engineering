package example;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
@RestController
@RequestMapping("/api")
public class StatusController {
    @GetMapping("/status")
    public String status() { return "development-scaffold"; }
}
