import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import FindWaldo from "./pages/FindWaldo";
import ErrorPage from "./ErrorPage";

const Router = () => {
    const router = createBrowserRouter([
        {
            path: "/",
            element: <App />,
            errorElement: <ErrorPage />,
        },
        {
            path: "find-waldo",
            element: <FindWaldo />,
        },
    ]);

    return <RouterProvider router={router} />;
};

export default Router;