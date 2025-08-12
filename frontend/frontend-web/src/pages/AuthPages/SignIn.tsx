import PageMeta from "../../components/common/PageMeta";
import AuthLayout from "./AuthPageLayout";
import SignInForm from "../../components/auth/SignInForm";

export default function SignIn() {
  const title = "Sign In | Vanta Ledger Dashboard";
  const description = "This is the Sign In page for the Vanta Ledger Dashboard.";
  return (
    <>
      <PageMeta
        title={title}
        description={description}
      />
      <AuthLayout>
        <SignInForm />
      </AuthLayout>
    </>
  );
}
