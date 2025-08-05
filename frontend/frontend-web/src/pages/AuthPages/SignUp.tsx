import PageMeta from "../../components/common/PageMeta";
import AuthLayout from "./AuthPageLayout";
import SignUpForm from "../../components/auth/SignUpForm";

export default function SignUp() {
  const title = "Sign Up | Vanta Ledger Dashboard";
  const description = "This is the Sign Up page for the Vanta Ledger Dashboard.";
  return (
    <>
      <PageMeta
        title={title}
        description={description}
      />
      <AuthLayout>
        <SignUpForm />
      </AuthLayout>
    </>
  );
}
