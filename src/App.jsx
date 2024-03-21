import waldoSRC from "./assets/wally.png";
import { useNavigate } from "react-router-dom";
import "./styles/index.css";
import Scores from "./pages/Scores";
const App = () => {
    const navigate = useNavigate();
    return (
        <div className="home">
            <div>
                <img src={waldoSRC} alt="" />
                <div className="tittle">
                    <h1>WHERE IS WALDO?</h1>
                    <p>
                        Try to find waldo, wizard and odlaw as soon as possible
                    </p>
                </div>

                <div>
                    <button onClick={() => navigate("/find-waldo")}>
                        PLAY NOW
                    </button>
                </div>
                <Scores />
            </div>
        </div>
    );
};

export default App;