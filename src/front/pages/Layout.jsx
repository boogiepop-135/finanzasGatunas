import { Outlet } from "react-router-dom"
import ScrollToTop from "../components/ScrollToTop"
import { Navbar } from "../components/Navbar"
import { Footer } from "../components/Footer"

// Base component that maintains the navbar and footer throughout the page and the scroll to top functionality.
export const Layout = () => {
    return (
        <div className="app-container">
            <ScrollToTop>
                <Navbar />
                <main className="flex-fill">
                    <Outlet />
                </main>
                <Footer />
            </ScrollToTop>
        </div>
    )
}