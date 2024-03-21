import waldoPic from "../assets/whereswaldo.jpg";
import waldoSRC from "../assets/wally-standing.png";
import wizardSRC from "../assets/wizard.gif";
import odlawSRC from "../assets/odlaw.gif";
import "../styles/find-waldo.css";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Popup from "reactjs-popup";
import Stopwatch from "../components/Watch";
import API_URL from "../assets/api-url";

const FindWaldo = () => {
    const picRef = useRef(null);
    const menuRef = useRef(null);
    const [foundWaldo, setFoundWaldo] = useState(false);
    const [foundWizard, setFoundWizard] = useState(false);
    const [foundOdlaw, setFoundOdlaw] = useState(false);
    const [open, setOpen] = useState(false);
    // state to check stopwatch running or not
    const [isRunning, setIsRunning] = useState(true);
    const userIDRef = useRef(null);
    const endDateRef = useRef(null);
    const navigate = useNavigate();
    let x;
    let y;
    async function sendRequest(character, setFoundCharacter) {
        console.log({ character, x, y });
        menuRef.current.style.display = "none";

        // Default options are marked with *
        const response = await fetch(
            API_URL + "/coordinates/" + character + "&" + x + "&" + y
        );
        const foundCharacter = await response.json();
        console.log(foundCharacter);
        if (foundCharacter) setFoundCharacter(true);
        return response; // parses JSON response into native JavaScript objects
    }
    async function registerUser() {
        // Default options are marked with *
        let result = await fetch(API_URL + "/users/", {
            method: "POST",
            mode: "cors",
        });
        const data = await result.json();
        userIDRef.current = data;
        return data; // parses JSON response into native JavaScript objects
    }
    async function postUserScore(userName) {
        // Default options are marked with *
        await fetch(API_URL + "/users/" + userIDRef.current, {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: userName,
                end_date: endDateRef.current,
            }),
        });
        //const content = await result.json();

        //console.log(content);
    }
    useEffect(() => {
        //START WHEN THE PAGE IS OPEN
        if (userIDRef.current === null) {
            registerUser();
        }
    }, []);
    useEffect(() => {
        //TRACK WHEN ALL THE CHARACTERS HAS BEEN FOUND
        if (foundWaldo & foundWizard & foundOdlaw) {
            setOpen(true);
            setIsRunning(false);
            endDateRef.current = new Date();
        }
    }, [foundWaldo, foundWizard, foundOdlaw]);
    //CAPTURE COORDINATE NO MATTER THE SIZE OF THE PICTURE
    function capturePosition(e) {
        x = Math.round(
            (100 * (e.pageX - e.currentTarget.offsetLeft)) /
            picRef.current.offsetWidth
        );
        y = Math.round(
            (100 * (e.pageY - e.currentTarget.offsetTop)) /
            picRef.current.offsetHeight
        );
        menuRef.current.style.display = "flex";
        menuRef.current.style.left =
            e.pageX - menuRef.current.offsetWidth / 2 + "px";
        menuRef.current.style.top = e.pageY - 25 + "px";
        console.log({ x: x, y: y });
    }
    function handleMouseLeaveEvent() {
        setTimeout(() => {
            menuRef.current.style.display = "none";
        }, 200);
    }
    return (
        <div className="game-container">
            <div className="header tittle">
                <h1>WHERE IS WALDO?</h1>
                <p>Try to find waldo, wizard and odlaw as soon as possible</p>
            </div>
            <Characters
                foundWaldo={foundWaldo}
                foundWizard={foundWizard}
                foundOdlaw={foundOdlaw}
                setOpen={setOpen}
                isRunning={isRunning}
                setIsRunning={setIsRunning}
            />
            <div className="pic-container">
                <img
                    src={waldoPic}
                    alt="illustration of many people in a beach"
                    onClick={(e) => {
                        capturePosition(e);
                    }}
                    ref={picRef}
                />
                <div
                    className="menu"
                    ref={menuRef}
                    onMouseLeave={handleMouseLeaveEvent}
                >
                    <div className="target"></div>
                    <nav>
                        <button
                            onClick={() => sendRequest("waldo", setFoundWaldo)}
                        >
                            Waldo
                        </button>
                        <button
                            onClick={() =>
                                sendRequest("wizard", setFoundWizard)
                            }
                        >
                            Wizard
                        </button>
                        <button
                            onClick={() => sendRequest("odlaw", setFoundOdlaw)}
                        >
                            Odlaw
                        </button>
                    </nav>
                </div>
            </div>
            <Popup open={open} modal nested>
                <div className="popup">
                    <h1>You win!</h1>
                    <p>Please insert a nickname</p>
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            postUserScore(e.target.nickname.value);
                            navigate("/");
                        }}
                    >
                        <label hidden htmlFor="nickname">
                            nickname
                        </label>
                        <input type="text" name="nickname" />
                        <button>Send</button>
                    </form>
                </div>
            </Popup>
        </div>
    );
};

function Characters(prob) {
    return (
        <div className="characters-container">
            <img
                src={waldoSRC}
                alt=""
                style={{ opacity: prob.foundWaldo ? "0.5" : "1" }}
            />
            <h2 style={{ color: prob.foundWaldo ? "#39e47a" : null }}>
                Waldo{prob.foundWaldo ? "✓" : null}
            </h2>
            <img
                src={wizardSRC}
                alt=""
                style={{ opacity: prob.foundWizard ? "0.5" : "1" }}
            />
            <h2 style={{ color: prob.foundWizard ? "#39e47a" : null }}>
                Wizard{prob.foundWizard ? "✓" : null}
            </h2>
            <img
                src={odlawSRC}
                alt=""
                style={{ opacity: prob.foundOdlaw ? "0.5" : "1" }}
            />
            <h2 style={{ color: prob.foundOdlaw ? "#39e47a" : null }}>
                Odlaw{prob.foundOdlaw ? "✓" : null}
            </h2>
            <Stopwatch
                isRunning={prob.isRunning}
                setIsRunning={prob.setIsRunning}
            />
        </div>
    );
}

export default FindWaldo;